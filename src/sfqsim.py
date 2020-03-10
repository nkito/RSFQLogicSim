# -*- encoding: utf-8 -*-

import sys
import sfqsim_yacc


def error_exit():
    print('RSFQ logic simulation tool \n', file=sys.stderr)
    print('Usage: python3 {} [input sfqv file] \n'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)



if __name__ == '__main__':
    param = sys.argv

    debug = False

    if len(param) >= 2 :
        for i in range(1,len(param)):
            if param[i] == "-debug":
                debug = True
            elif param[i].startswith("-"):
                error_exit()
            else:
                file = open(param[i], 'rt')
                source_input = file.read()
                file.close()
                sfqsim_yacc.parse_and_execute( source_input, debug = debug )
    else :
        error_exit()

