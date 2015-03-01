# coding: utf8

tokens = (
    'STRING_LITERAL',
    'IDENTIFIER',
)

t_STRING_LITERAL = r'"[^\n\\]*"'

t_IDENTIFIER = r'[_a-zA-Z가-힣][a-zA-Z가-힣0-9_]*'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("잘못된 문자입니다: {}".format(repr(t.value[0])))
    t.lexer.skip(1)


import ply.lex
ply.lex.lex()
