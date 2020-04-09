# check if the list 'a' is included in list 'b'
def is_included(a, b):
    for item in a:
        if item not in b:
            return False

    return True


# check if lists 'a' and 'b' are disjoint
def is_disjoint(a, b):
    for item in a:
        if item in b:
            return False
    return True