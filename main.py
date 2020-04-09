import Tkinter, tkFileDialog
import copy
from utils import is_disjoint
from utils import is_included
from input_rewriting import *
from backward_slicing import backward_slicing

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

ur = ua_to_dict(ua)
ca = rewrite_ca(ca)
cr = rewrite_cr(cr)

# In order to simplify the instances of the role reachability problem some roles and users are removed
# by applying the backward slicing
backward_result = backward_slicing(goal, ca, cr, ur, roles)

ca = backward_result["ca"]
cr = backward_result["cr"]
roles = backward_result["roles"]
ur = backward_result["ur"]


# given a list of user-to-role assignments, returns all the possible revocable roles
# in the following form: [(user_a, role_a), ..., (user_n, role_n)],
# a rule admits to revoke role_a to user_a, ..., role_n to user_n
def can_revoke_roles(ur_param):
    res = []
    ru = ru_from_ur(ur_param)

    for cr_rule in cr:
        for user_a, roles_a in ur_param.items():
            if cr_rule["ra"] in roles_a and cr_rule["rt"] in ru:
                for user_t in ru[cr_rule["rt"]]:
                    res += [(user_t, cr_rule["rt"])]

    return res


# given a list of user-to-role assignments, returns all the possible assignable roles
# in the following form: [(user_a, role_a), ..., (user_n, role_n)],
# a rule admits to assign role_a to user_a, ..., role_n to user_n
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


# returns 1 if the goal role is reachable, 0 otherwise
# params:
# - ur_param: the user to role assignment
# - configurations: the configurations already tested from which it is not possible to reach the goal
def is_reachable(ur_param, configurations):
    ur_copy = copy.deepcopy(ur_param)
    ru = ru_from_ur(ur_copy)

    if goal in ru and ru[goal]:
        return 1

    can_ass_list = can_assign_roles(ur_copy)

    for ass in can_ass_list:

        if ass[0] not in ur_copy:
            ur_copy[ass[0]] = []
        ur_copy[ass[0]] += [ass[1]]

        ex = True
        for conf in configurations:
            if conf == ur_copy:
                ex = False

        if ex:
            if is_reachable(ur_copy, configurations) == 1:
                return 1
            else:
                to_add = copy.deepcopy(ur_copy)
                configurations += [to_add]

        ur_copy[ass[0]].remove(ass[1])

    can_rev_list = can_revoke_roles(ur_copy)

    for rev in can_rev_list:
        ur_copy[rev[0]].remove(rev[1])

        ex = True
        for conf in configurations:
            if conf == ur_copy:
                ex = False

        if ex:
            if is_reachable(ur_copy, configurations) == 1:
                return 1
            else:
                to_add = copy.deepcopy(ur_copy)
                configurations += [to_add]

        ur_copy[rev[0]] += [rev[1]]

    return 0


# call to the recursive function
print(is_reachable(ur, []))




