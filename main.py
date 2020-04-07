import Tkinter, tkFileDialog

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


# roles = partitioned_text[0].replace(" ;", "").split(" ")
# users = partitioned_text[1].replace(" ;", "").split(" ")
# ua = partitioned_text[2].replace(" ;", "").split(" ")
# cr = partitioned_text[3].replace(" ;", "").split(" ")
# ca = partitioned_text[4].replace(" ;", "").split(" ")
# goal = partitioned_text[5].replace(" ;", "").split(" ")[0]


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


def ru_from_ur(ur):
    dict = {}
    for user, roles in ur.items():
        for role in roles:
            if role not in dict:
                dict[role] = []
            dict[role] += [user]
    return dict


ur = ua_to_dict(ua)
ca = rewrite_ca(ca)
cr = rewrite_cr(cr)


def get_next(before, ca):
    res = before
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
ca = aux

aux = []
for cr_rule in cr:
    if cr_rule["rt"] in s:
        aux.append(cr_rule)
cr = aux

aux = []
for role in roles:
    if role in s:
        aux.append(role)
roles = aux

for user, r in ur.items():
    aux = []
    for role in r:
        if role in s:
            aux.append(role)
    r = aux

def can_revoke_roles(cr, ur):
    res = []
    ru = ru_from_ur(ur)

    for cr_role in cr:
        for user_a, roles_a in ur.items():
            if cr_role["ra"] in roles_a and cr_role["rt"] in ru:
                for user_t in ru[cr_role["rt"]]:
                    res += [(user_t, cr_role["rt"])]

    return res


def can_assign_roles(ca, ur, users):
    res = []
    ru = ru_from_ur(ur)

    for ca_role in ca:
        for user_a_ur, roles_a_ur in ur.items():
            if ca_role["ra"] in roles_a_ur:
                for user_t in users:
                    if not user_t in ur or (
                            all(elem in ur[user_t] for elem in ca_role["Rp"]) and set(ur[user_t]).isdisjoint(
                        ca_role["Rn"]) and ca_role["rt"] not in ur[user_t]):
                        res += [(user_t, ca_role["rt"])]
    return res

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def is_reachable(goal, ca, ur, users, already_add, already_remove):
    ru = ru_from_ur(ur)
    if goal in ru and ru[goal]:
        return 1

    can_ass_list = can_assign_roles(ca, ur, users)

    for ass in can_ass_list:
        if ass[0] not in already_add or ass[1] not in already_add[ass[0]]:
            if ass[0] not in ur:
                ur[ass[0]] = []
            ur[ass[0]] += [ass[1]]

            if ass[0] not in already_add:
                already_add[ass[0]] = []
            already_add[ass[0]] += [ass[1]]

            val = is_reachable(goal, ca, ur, users, already_add, already_remove)
            if val == 1:
                return val

            ur[ass[0]].remove(ass[1])
            already_add[ass[0]].remove(ass[1])

    can_rev_list = can_revoke_roles(cr, ur)
    for rev in can_rev_list:
        if rev[0] not in already_remove or rev[1] not in already_remove[rev[0]]:
            ur[rev[0]].remove(rev[1])

            if rev[0] not in already_remove:
                already_remove[rev[0]] = []
            already_remove[rev[0]] += [rev[1]]

            val = is_reachable(goal, ca, ur, users, already_add, already_remove)

            if val == 1:
                return 1

            ur[rev[0]] += [rev[1]]
            already_remove[rev[0]].remove(rev[1])

    return 0


if is_reachable(goal, ca, ur, users, {}, {}) > 0:
    print(1)
else:
    print(0)





