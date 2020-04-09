import Tkinter, tkFileDialog
import copy

root = Tkinter.Tk()
root.withdraw()

file_path = tkFileDialog.askopenfilename()

f = open(file_path, "r")
text = f.read()

partitioned_text = text.split('\n')

roles = partitioned_text[0].replace(" ;", "").replace("Roles ", "").split(" ")
users = partitioned_text[2].replace(" ;", "").replace("Users ", "").split(" ")
ua = partitioned_text[4].replace(" ;", "").replace("UA ", "").split(" ")
cr = partitioned_text[6].replace(" ;", "").replace("CR ", "").split(" ")
ca = partitioned_text[8].replace(" ;", "").replace("CA ", "").split(" ")
goal = partitioned_text[10].replace(" ;", "").replace("Goal ", "").split(" ")[0]


def ua_to_dict(ua):
    dict = {}
    for item in ua:
        item = item.replace("<", "").replace(">", "").split(",")
        user = item[0]
        role = item[1]
        if user not in dict:
            dict[user] = []
        dict[user] += [role]
    return dict


def get_ca_roles(a):
    ret = [[], []]
    if a == "TRUE":
        return ret
    a = a.split("&")
    for item in a:
        if item[0] != "-":
            ret[0] += [item]
        else:
            ret[1] += [item[1:]]
    return ret


def get_necessary_roles(a):
    return get_ca_roles(a)[0]


def get_absent_roles(a):
    return get_ca_roles(a)[1]


def rewrite_ca(ca):
    arr = []
    for item in ca:
        dict = {}
        item = item.replace("<", "").replace(">", "").split(",")
        dict["ra"] = item[0]
        dict["Rp"] = get_necessary_roles(item[1])
        dict["Rn"] = get_absent_roles(item[1])
        dict["rt"] = item[2]
        arr += [dict]
    return arr


def rewrite_cr(cr):
    arr = []
    for item in cr:
        dict = {}
        item = item.replace("<", "").replace(">", "").split(",")
        dict["ra"] = item[0]
        dict["rt"] = item[1]
        arr += [dict]
    return arr


def ru_from_ur(ur_param):
    d = {}
    for u, rs in ur_param.items():
        for r in rs:
            if r not in d:
                d[r] = []
            d[r] += [u]
    return d


ur = ua_to_dict(ua)
ca = rewrite_ca(ca)
cr = rewrite_cr(cr)

def get_next(before, ca):
    res = copy.deepcopy(before)
    for ca_rule in ca:
        if ca_rule["rt"] in before:
            res = res + ca_rule["Rp"] + ca_rule["Rn"] + [ca_rule["ra"]]
    return res


s = []
s.append([goal])
s.append(get_next(s[0], ca))
i = 1
while set(s[i]) != set(s[i - 1]):
    s.append(get_next(s[i], ca))
    i += 1

s = s[-1]

aux = []
for ca_rule in ca:
    if ca_rule["rt"] in s:
        aux.append(ca_rule)
ca = copy.deepcopy(aux)

aux = []
for cr_rule in cr:
    if cr_rule["rt"] in s:
        aux.append(cr_rule)
cr = copy.deepcopy(aux)

aux = []
for role in roles:
    if role in s:
        aux.append(role)
roles = copy.deepcopy(aux)

for user, rs in ur.items():
    aux = []
    for role in rs:
        if role in s:
            aux.append(role)
    ur[user] = copy.deepcopy(aux)


def can_revoke_roles(ur_param):
    res = []
    ru = ru_from_ur(ur_param)

    for cr_rule in cr:
        for user_a, roles_a in ur_param.items():
            if cr_rule["ra"] in roles_a and cr_rule["rt"] in ru:
                for user_t in ru[cr_rule["rt"]]:
                    res += [(user_t, cr_rule["rt"])]

    return res


def is_included(a, b):
    for item in a:
        if item not in b:
            return False

    return True


def is_disjoint(a, b):
    for item in a:
        if item in b:
            return False
    return True


def can_assign_roles(ur_param):
    res = []

    for ca_rule in ca:
        for user_a_ur, roles_a_ur in ur_param.items():
            if ca_rule["ra"] in roles_a_ur:
                for user_t in users:
                    if user_t not in ur_param or (
                            is_included(ca_rule["Rp"], ur_param[user_t]) and is_disjoint(
                            ca_rule["Rn"], ur_param[user_t]) and ca_rule["rt"] not in ur_param[user_t]):
                        res += [(user_t, ca_rule["rt"])]
    return res


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def is_reachable(ur_param, to_print, configurations):
    ur_copy = copy.deepcopy(ur_param)
    ru = ru_from_ur(ur_copy)

    if goal in ru and ru[goal]:
        return 1

    can_ass_list = can_assign_roles(ur_copy)
    i = 1

    for ass in can_ass_list:
        if ass[1] == goal:
            return 1

        if ass[0] not in ur_copy:
            ur_copy[ass[0]] = []
        ur_copy[ass[0]] += [ass[1]]

        ex = True
        for conf in configurations:
            if conf == ur_copy:
                ex = False

        if to_print:
            print(str(i)+" out of "+str(len(can_ass_list)))
            i += 1

        if ex:
            val = is_reachable(ur_copy, False, configurations)
            if val == 1:
                return val
            else:
                to_add = copy.deepcopy(ur_copy)
                configurations += [to_add]

        ur_copy[ass[0]].remove(ass[1])

    i = 1
    can_rev_list = can_revoke_roles(ur_copy)

    for rev in can_rev_list:
        ur_copy[rev[0]].remove(rev[1])

        ex = True
        for conf in configurations:
            if conf == ur_copy:
                ex = False

        if to_print:
            print(str(i)+" out of "+str(len(can_rev_list)))
            i += 1

        if ex:
            val = is_reachable(ur_copy, False, configurations)

            if val == 1:
                return 1
            else:
                to_add = copy.deepcopy(ur_copy)
                configurations += [to_add]

        ur_copy[rev[0]] += [rev[1]]

    return 0


if is_reachable(ur, True, []) > 0:
    print(1)
else:
    print(0)





