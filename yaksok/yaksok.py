import sys

import yacc


def main():
    if len(sys.argv) > 1:
        code = open(sys.argv[1]).read()
        yacc.parse(code)
        return
    while True:
        try:
            code = input('> ')
        except EOFError:
            print('')
            break
        yacc.parse(code)


if __name__ == '__main__':
    main()
