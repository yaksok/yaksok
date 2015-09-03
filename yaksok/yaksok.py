import argparse
import os
import sys
import copy

from . import yacc
from . import bootbakyi

def run_code(code, file_name = None):
    code = yacc.compile_code(code, file_name=file_name)

    locals_dict = {}
    g = copy.deepcopy(yaksok_globals)
    locals_dict['____functions'] = g['____functions']
    if file_name is None:
        exec(code, g, locals_dict)
        return locals_dict
    else:
        exec(code, g, g)
        return g


bootbakyi.____run_code = run_code
bootbakyi.____libpath = os.path.join(os.path.split(__file__)[0], 'modules')


yaksok_globals = {k:getattr(bootbakyi, k) for k in dir(bootbakyi)}


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('file_name', nargs='?')
    argparser.add_argument('-d', '--debug', action='store_true')
    argparser.add_argument('-p', '--path', action='store', default='')
    args = argparser.parse_args()
    if args.path:
        os.chdir(args.path)
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    if args.file_name:
        code = open(args.file_name).read()
        run_code(code, args.file_name)
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
