보여주기 = print
____range = range
def ____subscript(l, x):
    if isinstance(x, (list, range)):
        if isinstance(l, str):
            return ''.join(l[y-1] for y in x)
        else:
            return [l[y-1] for y in x]
    else:
        return l[x-1]

