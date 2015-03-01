# coding: utf8

tokens = (
    'INTEGER',
    'STRING_LITERAL',
    'IDENTIFIER',

    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
)

t_INTEGER = r'[0-9]+'
t_STRING_LITERAL = r'"[^\n\\]*"'

t_IDENTIFIER = r'[_a-zA-Z가-힣][a-zA-Z가-힣0-9_]*'

t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULT = r'\*'
t_DIV = r'/'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("잘못된 문자입니다: {}".format(repr(t.value[0])))
    t.lexer.skip(1)


import ply.lex
ply.lex.lex()
