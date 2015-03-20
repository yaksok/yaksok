없음 = None
____id = id
____debug = False
____locals = locals
____globals = globals
____range = range
____eval = eval
____modules = {}

def ____getmodule(name):
    # TODO sys.modules 같은 import된 모듈 저장소가 필요
    if name not in ____modules:
        ____modules[name] = ____run_code(open(name + '.yak').read(), name+'.yak')
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

def ____find_and_call_function(matcher, lenv, genv, functions):
    def has_variable(x):
        return x in genv or x in lenv

    def get_variable_value(x):
        if x in lenv:
            return lenv[x]
        return genv[x]
        #if x in locals():
            #return locals()[x]
        #return globals()[x]

    def try_match(matcher, proto):
        if ____debug:
            print('try_match', matcher, proto)
        if not matcher and not proto:
            yield []
            return
        if not matcher and proto:
            return
        if matcher and not proto:
            return
        if matcher[0][0] == 'EXPR':
            if ____debug:
                print('\t1')
            if proto[0][0] == 'IDENTIFIER':
                skip = 1
                if len(proto) >= 2 and proto[1][0] == 'WS':
                    skip = 2
                for sub_candidate in try_match(matcher[1:], proto[skip:]):
                    yield [matcher[0][1]] + sub_candidate
        else: # matcher[0][0] == 'NAME'
            if proto[0][0] == 'IDENTIFIER':
                if ____debug:
                    print('\t21')
                sole_variable_exists = False
                # 전체 이름에 해당하는 변수가 존재
                if ____debug:
                    print('\t',matcher[0][1],has_variable(matcher[0][1]))
                if has_variable(matcher[0][1]):
                    sole_variable_exists = True
                    skip = 1
                    if len(proto) >= 2 and proto[1][0] == 'WS':
                        skip = 2
                    for sub_candidate in try_match(matcher[1:], proto[skip:]):
                        yield [get_variable_value(matcher[0][1])] + sub_candidate

                # 정의에 빈칸 없는 경우, 잘라서 시도해본다
                if len(proto) >= 2 and proto[1][0] != 'WS':
                    if ____debug:
                        print('\tsplit',matcher[0][1],proto[1][1])
                    if proto[1][0] == 'STR' and matcher[0][1].endswith(proto[1][1]):
                        variable_name = matcher[0][1][:-len(proto[1][1])];
                        if has_variable(variable_name):
                            skip = 2
                            if len(proto) >= 3 and proto[2][0] == 'WS':
                                skip = 3
                            for sub_candidate in try_match(matcher[1:], proto[skip:]):
                                if sole_variable_exists:
                                    raise SyntaxError("헷갈릴 수 있는 변수명이 사용됨: " + matcher[0][1] + " / " + variable_name + "+" + proto[1][1])
                                yield [get_variable_value(variable_name)] + sub_candidate
            elif proto[0][0] == 'STR':
                if ____debug:
                    print('\t22')
                if matcher[0][1] == proto[0][1]:
                    skip = 1
                    if len(proto) >= 2 and proto[1][0] == 'WS':
                        skip = 2
                    for sub_candidate in try_match(matcher[1:], proto[skip:]):
                        yield sub_candidate

            else:
                pass


    candidates = []
    for func, proto in functions:
        for args in try_match(matcher, proto):
            candidates.append((func, args))

    if len(candidates) == 0:
        raise SyntaxError("해당하는 약속을 찾을 수 없습니다.")
    if len(candidates) >= 2:
        raise SyntaxError("적용할 수 있는 약속이 여러개입니다.")

    func, args = candidates[0]
    return func(*args)


____functions = [(____print_one, [('IDENTIFIER', '값'), ('WS',' '), ('STR', '보여주기')])]
