#!/usr/bin/python

import sys

import ply.yacc as yacc
import ply.lex as lex

from trainingsession import tools as t


""" LEXER SPECS """
tokens = (
    'RUN', 'FLOAT_VAL', 'INT_VAL', 'REPEAT', 'KM', 'KMH', 'PERCENT', 'INDEF',
    'AT', 'TIME_VALS', 'LBRACKET', 'RBRACKET', 'SEMI', 'TIME_VAL', 'PREFIX',
    'MORELESS'
)

t_RUN = r'run'
t_REPEAT = r'repeat'
t_KM = r'km'
t_KMH = r'kmh'
t_PERCENT = r'%'
t_INDEF = r'indefinitely'
t_AT = r'at'
t_TIME_VALS = r'times'
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_SEMI = r';'
t_PREFIX = r'\(\w+\)'
t_MORELESS = r'\+-'
t_ignore = " \t"
t_ignore_COMMENT = r'\#.*'


def t_FLOAT_VAL(t):
    r'\d+\.\d+'

    t.value = float(t.value)
    return t


def t_TIME_VAL(t):
    r'[0-9]+m[0-9]+s'

    # remove 'm' and 's' from string and return the value in seconds
    mins, secs = t.value.split('m')
    secs = secs[:-1]
    t.value = int(mins) * 60 + int(secs)
    return t


def t_INT_VAL(t):
    r'\d+'

    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'

    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


"""PARSER SPECS"""


def p_trainingSession(p):
    '''trainingSession : step SEMI
                      | step SEMI trainingSession'''

    # return the session : a list of steps (runStep or repeat)
    if len(p) == 3:
        p[0] = [p[1]]
    else:
        session = p[3]
        session.insert(0, p[1])
        p[0] = session


def p_step(p):
    '''step : RUN duration prefix
            | RUN duration AT target prefix
            | REPEAT INT_VAL TIME_VALS LBRACKET trainingSession RBRACKET'''

    if len(p) == 4:
        kwargs = dict(p[2], **p[3])  # combine the two dicts of argument
        remaining = t.Remaining(**kwargs)
        p[0] = t.RunStep(remaining)
    elif len(p) == 6:
        kwargs = dict(p[2], **p[5])  # combine the two dicts of arguments
        remaining = t.Remaining(**kwargs)
        p[0] = t.RunStep(remaining, p[4])
    else:
        p[0] = t.Repeat(p[2], p[5])


def p_prefix(p):
    '''prefix : PREFIX
              | '''
    if len(p) == 2:
        # remove parenteses and set prefix argument
        p[0] = {'prefix': '"' + p[1][1:-1] + '"'}
    else:
        p[0] = {}


def p_target_percent(p):
    '''target : INT_VAL PERCENT margin
              | FLOAT_VAL KMH margin
              | INT_VAL KMH margin '''

    kwargs = p[3]  # the margin
    if p[2] == '%':
        p[0] = t.Target(hr=p[1], **kwargs)
    else:
        p[0] = t.Target(spd=p[1], **kwargs)


def p_margin(p):
    '''margin : MORELESS INT_VAL
              | MORELESS FLOAT_VAL
              | '''
    if len(p) == 3:
        p[0] = {'margin': p[2]}
    else:
        p[0] = {}


def p_duration(p):
    '''duration : FLOAT_VAL KM
                | INT_VAL KM
                | INDEF
                | TIME_VAL'''

    if len(p) == 3:
        p[0] = {'dist': p[1]}
    elif p[1] == 'indefinitely':
        p[0] = {'lap': True}
    else:
        p[0] = {'dur': p[1]}


def p_error(p):

    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


"""MAIN PROGRAM"""

if len(sys.argv) != 2:
    exit('Usage: python -m traininsession <session_script>')
else:
    inFile = open(sys.argv[1], 'r')

lex.lex()  # build lexer
yacc.yacc()  # build parser

# read and parse input file
# result is in the 'session' list containing training steps

session = yacc.parse(inFile.read())
inFile.close()

print("Remaning app, showing how much time/distance is left:")
print(t.applicationCode(session))
print("-" * 30)
print("Target app, showing if you're higher or lower than your target:")
print(t.applicationCode(session, appType='target'))
