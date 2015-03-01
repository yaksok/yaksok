import sys

import yacc


yaksok_globals = {
    '__builtins__': {
        '보여주기': print,
    },
}


def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        code = open(file_name).read()
        code = yacc.compile_code(code, file_name=file_name)
        exec(code, yaksok_globals)
        return
    while True:
        try:
            code = input('> ')
        except EOFError:
            print('')
            break
        code = yacc.compile_code(code)
        exec(code, yaksok_globals)


if __name__ == '__main__':
    main()
