# -*- encoding: utf-8 -*-

import ply.lex as lex
import sys

tokens = (
    'NUMBER',
    'LBRACE',
    'RBRACE',
    'LPAREN',
    'RPAREN',
    'LBLOCK',
    'RBLOCK',
    'SEMI',
    'COLON',
    'COMMA',
    'SYM_CONST',
    'SYM_INPUT',
    'SYM_OUTPUT',
    'SYM_WIRE',
    'SYM_ASSIGN',
    'SYM_MODULE',
    'SYM_ENDMODULE',
    'SYM_GENVAR',
    'SYM_FOR',
    'SYM_EQEQ',
    'SYM_PEQ',
    'SYM_NEQ',
    'SYM_EQ',
    'SYM_AT',
    'SYM_LT',
    'SYM_GT',
    'SYM_PLUS',
    'SYM_MINUS',
    'SYM_STAR',
    'SYM_SLASH',
    'NAME',
    'CONST_REF',
)

t_NUMBER        = r'[0-9]|[1-9][0-9]+'
t_LBRACE        = '{'
t_RBRACE        = '}'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_LBLOCK        = r'\['
t_RBLOCK        = r'\]'
t_SEMI          = ';'
t_COLON         = ':'
t_COMMA         = ','
t_SYM_CONST     = r'const'
t_SYM_INPUT     = r'input'
t_SYM_OUTPUT    = r'output'
t_SYM_WIRE      = r'wire'
t_SYM_ASSIGN    = r'assign'
t_SYM_MODULE    = r'module'
t_SYM_ENDMODULE = r'endmodule'
t_SYM_GENVAR    = r'genvar'
t_SYM_FOR       = r'for'
t_SYM_EQEQ      = r'\=\='
t_SYM_PEQ       = r'\+\='
t_SYM_NEQ       = r'\!\='
t_SYM_EQ        = r'\='
t_SYM_AT        = r'\@'
t_SYM_LT        = r'\<'
t_SYM_GT        = r'\>'
t_SYM_PLUS      = r'\+'
t_SYM_MINUS     = r'\-'
t_SYM_STAR      = r'\*'
t_SYM_SLASH     = r'\/'

t_NAME      = '(?!const|input|output|wire|assign|module|endmodule|genvar|for)[_a-zA-Z][_a-zA-Z0-9]*'
t_CONST_REF = '\`[_a-zA-Z][_a-zA-Z0-9]*'

t_ignore_COMMENT = r'/\*[\s\S]*?\*/|//.*|\#.*'
t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Error: illegal character '%s'" % t.value[0], file=sys.stderr)
    t.lexer.skip(1)


lexer = lex.lex()


def lex_test( data ):

    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok: 
            break
        print(tok)


if __name__ == '__main__':
    param = sys.argv

    if len(param) == 2 :
        file = open(param[1], 'rt')
        source_input = file.read()
        file.close()
    else :
        source_input = sys.stdin.read()

    lex_test( source_input )

