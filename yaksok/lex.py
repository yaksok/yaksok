# coding: utf8

import ply.lex

TAB_SIZE = 8
must_indent_group = set(["THEN", "LOOP"])

reserved = {
    '만약':'IF',
    '이면':'THEN',
    '이라면':'THEN',
    '참':'TRUE',
    '거짓':'FALSE',
    '반복':'LOOP',
}

tokens = [
    'INTEGER',
    'STRING_LITERAL',
    'IDENTIFIER',

    'ASSIGN',
    'COMMA',
    'TILDE',

    'PLUS',
    'MINUS',
    'MULT',
    'DIV',

    'EQ',
    'GT',
    'LT',

    'LPAR',
    'RPAR',
    'LSQUARE',
    'RSQUARE',

    'NEWLINE',
    'INDENT',
    'DEDENT',
    'WS',

    'ENDMARKER',
] + list(set(reserved.values()))


def t_comment(t):
    r"[ ]*\#[^\n]*"
    pass


def t_WS(t):
    r'[ \t]+'
    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        t.value = t.value.replace('\t', ' '*TAB_SIZE)
        return t


t_INTEGER = r'[0-9]+'
t_STRING_LITERAL = r'"[^\n\\\"]*"'

def t_IDENTIFIER(t):
    r'[_a-zA-Z가-힣][a-zA-Z가-힣0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

t_ASSIGN = r':'
t_COMMA = r','
t_TILDE = r'~'

t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULT = r'\*'
t_DIV = r'/'

t_EQ = '='
t_GT = '>'
t_LT = '<'

#t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    t.type = 'NEWLINE'
    if t.lexer.paren_count == 0:
        return t


def t_LSQUARE(t):
    r'\['
    t.lexer.paren_count += 1
    return t


def t_RSQUARE(t):
    r'\]'
    t.lexer.paren_count -= 1
    return t


def t_LPAR(t):
    r'\('
    t.lexer.paren_count += 1
    return t


def t_RPAR(t):
    r'\)'
    t.lexer.paren_count -= 1
    return t


def t_error(t):
    print("잘못된 문자입니다: {}".format(repr(t.value[0])))
    t.lexer.skip(1)

## from http://www.juanjoconti.com.ar/files/python/ply-examples/GardenSnake/GardenSnake.py.html

## I implemented INDENT / DEDENT generation as a post-processing filter

# The original lex token stream contains WS and NEWLINE characters.
# WS will only occur before any other tokens on a line.

# I have three filters.  One tags tokens by adding two attributes.
# "must_indent" is True if the token must be indented from the
# previous code.  The other is "at_line_start" which is True for WS
# and the first non-WS/non-NEWLINE on a line.  It flags the check so
# see if the new line has changed indication level.

# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent
NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line
def track_tokens_filter(lexer, tokens):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    saw_colon = False
    for token in tokens:
        token.at_line_start = at_line_start

        if token.type in must_indent_group:
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False

        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        else:
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start


def _new_token(type, lineno):
    tok = ply.lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    return tok


# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT", lineno)


# Synthesize an INDENT tag
def INDENT(lineno):
    return _new_token("INDENT", lineno)


# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in tokens:
##        if 1:
##            print "Process", token,
##            if token.at_line_start:
##                print "at_line_start",
##            if token.must_indent:
##                print "must_indent",
##            print

        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            # WS tokens are never passed to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise IndentationError("expected an indented block")

            levels.append(depth)
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                raise IndentationError("indentation increase but not in new block")
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    raise IndentationError("inconsistent indentation")
                for _ in range(i+1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    ### Finished processing ###

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)


def filter(lexer, add_endmarker = True):
    token = None
    tokens = iter(lexer.token, None)
    tokens = track_tokens_filter(lexer, tokens)
    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno)


class IndentLexer(object):
    def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
        self.lexer = ply.lex.lex(debug=debug, optimize=optimize, lextab=lextab, reflags=reflags)
        self.token_stream = None

    def input(self, s, add_endmarker=True):
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = filter(self.lexer, add_endmarker)

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None
