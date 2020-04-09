# rewrite the ua specification given in input as a dictionary
# The returned value has the following form:
# {user1:[role_a, ..., role_x], ...}
# for each user (the key) a list of roles is specified (the values)
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


# rewrite the Rp and Rn sets of each Can Assign rule in input
# The returned value has the following form:
# [ list of necessary roles, list of roles that must be absent ]
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


# returns the list of necessary roles of a given Can Assign rule in input
def get_necessary_roles(a):
    return get_ca_roles(a)[0]


# returns the list of roles that must be absent of a given Can Assign rule in input
def get_absent_roles(a):
    return get_ca_roles(a)[1]


# rewrite the Can Assign rule as a list of dictionaries.
# The returned value has the following form:
# [{ra: user_assigning_the_role, Rp: [necessary roles], Rn: [roles that must be absent], rt: user_receiving_the_role}, ...]
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


# rewrite the Can Revoke rule as a list of dictionary.
# The returned value has the following form:
# [{ra: user_revoking_the_role, rt: user_whose_role_is_removed}, ...]
def rewrite_cr(cr):
    arr = []
    for item in cr:
        dict = {}
        item = item.replace("<", "").replace(">", "").split(",")
        dict["ra"] = item[0]
        dict["rt"] = item[1]
        arr += [dict]
    return arr


# return a dictionary containing the role to users assignment
# The returned value has the following form:
# {role_a: [user1, ..., userN], ...}
def ru_from_ur(ur_param):
    d = {}
    for u, rs in ur_param.items():
        for r in rs:
            if r not in d:
                d[r] = []
            d[r] += [u]
    return d
