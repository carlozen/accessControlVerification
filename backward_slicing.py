import copy


def backward_slicing(goal, ca, cr, ur, roles):
    backward_result = {}

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
    backward_result["ca"] = copy.deepcopy(aux)

    aux = []
    for cr_rule in cr:
        if cr_rule["rt"] in s:
            aux.append(cr_rule)
    backward_result["cr"] = copy.deepcopy(aux)

    aux = []
    for role in roles:
        if role in s:
            aux.append(role)
    backward_result["roles"] = copy.deepcopy(aux)

    for user, rs in ur.items():
        aux = []
        for role in rs:
            if role in s:
                aux.append(role)
        ur[user] = copy.deepcopy(aux)

    backward_result["ur"] = ur

    return backward_result
