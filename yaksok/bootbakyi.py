없음 = None
____id = id
____debug = False
____locals = locals
____globals = globals
____range = range
____eval = eval
____modules = {}

def ____search_module_file(name):
    import os
    if os.path.exists(name + '.yak'):
        return name + '.yak'
    try:
        libpath = os.path.join(____libpath, name+'.yak')
        if os.path.exists(libpath):
            return libpath
    except:
        raise

    return name + '.yak'

def ____getmodule(name):
    # TODO sys.modules 같은 import된 모듈 저장소가 필요
    if name not in ____modules:
        path = ____search_module_file(name)
        ____modules[name] = ____run_code(open(path).read(), name+'.yak')
    return ____modules[name]


def ____subscript(l, x):
    if isinstance(x, (list, range)):
        if isinstance(l, str):
            return ''.join(l[y-1] for y in x)
        else:
            return [l[y-1] for y in x]
    else:
        if x > 0:
            x -= 1
        return l[x]

def ____print_one(x):
    print(x)

def ____find_and_call_function(matcher, lenv, genv, functions, cache={}):
    #key = tuple(x if x[0] != 'EXPR' else ('EXPR', None) for x in matcher), tuple(tuple(x[1]) for x in functions), tuple(sorted(lenv.keys())), tuple(sorted(genv.keys()))

    # disable cache
    key=[]
    def has_variable(x):
        return x in genv or x in lenv

    def get_variable_value(x, lenv, genv):
        if x in lenv:
            return lenv[x]
        return genv[x]
        #if x in locals():
            #return locals()[x]
        #return globals()[x]

    def try_match(proto, mi=0, pi=0):
        if ____debug:
            print('try_match', matcher, proto)
        if len(matcher) == mi and len(proto) == pi:
            yield []
            return
        if len(matcher) == mi:
            return
        if len(proto) == pi:
            return
        if matcher[mi][0] == 'EXPR':
            if ____debug:
                print('\t1')
            if proto[pi][0] == 'IDENTIFIER':
                skip = 1
                if len(proto) >= pi+2 and proto[pi+1][0] == 'WS':
                    skip = 2
                for sub_candidate in try_match(proto, mi+1, pi+skip):
                    yield [lambda l,g,m:m[mi][1]] + sub_candidate
        else: # matcher[mi][0] == 'NAME'
            if proto[pi][0] == 'IDENTIFIER':
                if ____debug:
                    print('\t21')
                sole_variable_exists = False
                # 전체 이름에 해당하는 변수가 존재
                if ____debug:
                    print('\t',matcher[mi][1],has_variable(matcher[mi][1]))
                if has_variable(matcher[mi][1]):
                    sole_variable_exists = True
                    skip = 1
                    if len(proto) >= pi+2 and proto[pi+1][0] == 'WS':
                        skip = 2
                    for sub_candidate in try_match(proto, mi+1, pi+skip):
                        yield [lambda l, g, m:get_variable_value(m[mi][1], l, g)] + sub_candidate

                # 정의에 빈칸 없는 경우, 잘라서 시도해본다
                if len(proto) >= pi+2 and proto[pi+1][0] != 'WS':
                    def try_sliced_str_match(each_str):
                        if ____debug:
                            print('\tsplit',matcher[mi][1],each_str)
                        if matcher[mi][1].endswith(each_str):
                            variable_name = matcher[mi][1][:-len(each_str)];
                            if has_variable(variable_name):
                                skip = 2
                                if len(proto) >= pi+3 and proto[pi+2][0] == 'WS':
                                    skip = 3
                                for sub_candidate in try_match(proto, mi+1, pi+skip):
                                    if sole_variable_exists:
                                        raise SyntaxError("헷갈릴 수 있는 변수명이 사용됨: " + matcher[mi][1] + " / " + variable_name + "+" + each_str)
                                    yield [lambda l, g, m:get_variable_value(variable_name, l, g)] + sub_candidate
                    if proto[pi+1][0] == 'STRS':
                        for each_str in proto[pi+1][1]:
                            yield from try_sliced_str_match(each_str)
                    elif proto[pi+1][0] == 'STR':
                        yield from try_sliced_str_match(proto[pi+1][1])
            elif proto[pi][0] == 'STR':
                if ____debug:
                    print('\t22')
                if matcher[mi][1] == proto[pi][1]:
                    skip = 1
                    if len(proto) >= pi+2 and proto[pi+1][0] == 'WS':
                        skip = 2
                    for sub_candidate in try_match(proto, mi+1, pi+skip):
                        yield sub_candidate
            elif proto[pi][0] == 'STRS':
                if ____debug:
                    print('\t23')
                for each_str in proto[pi][1]:
                    if matcher[mi][1] == each_str:
                        skip = 1
                        if len(proto) >= pi+2 and proto[pi+1][0] == 'WS':
                            skip = 2
                        for sub_candidate in try_match(proto, mi+1, pi+skip):
                            yield sub_candidate
            else:
                pass


    candidates = []
    can_hash = True
    try:
        hash(key)
    except:
        can_hash = False
    if can_hash and key in cache:
        candidates = cache[key]
    else:
        for func, proto in functions:
            for args in try_match(proto):
                candidates.append((func, args))
        if can_hash:
            cache[key] = candidates

    if len(candidates) == 0:
        raise SyntaxError("해당하는 약속을 찾을 수 없습니다.")
    if len(candidates) >= 2:
        raise SyntaxError("적용할 수 있는 약속이 여러개입니다.")

    func, args = candidates[0]
    args = [x(lenv,genv,matcher) for x in args]
    return type(func)(func.__code__, genv)(*args)


____functions = [(____print_one, [('IDENTIFIER', '값'), ('WS',' '), ('STR', '보여주기')])]
