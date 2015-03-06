import argparse
import sys

import yacc

import bootbakyi

yaksok_globals = {
    '__builtins__':{k:getattr(bootbakyi, k) for k in dir(bootbakyi)}
}


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('file_name', nargs='?')
    argparser.add_argument('-d', '--debug', action='store_true')
    args = argparser.parse_args()
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    if args.file_name:
        code = open(args.file_name).read()
        code = yacc.compile_code(code, file_name=args.file_name)
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
