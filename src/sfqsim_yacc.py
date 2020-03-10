# -*- encoding: utf-8 -*-

import ply.yacc as yacc
from sfqsim_lex import tokens
import sys
import pprint

import sfqsim_gates

precedence = (
     ('left', 'SYM_EQ'),
     ('left', 'SYM_GT', 'SYM_LT', 'SYM_NEQ', 'SYM_PEQ', 'SYM_EQEQ'),
     ('left', 'SYM_PLUS', 'SYM_MINUS'),
     ('left', 'SYM_STAR', 'SYM_SLASH'),
 )
 

dConst = {}

def p_simulation(p):
    '''
    simulation : const_defs inputs outputs modules  LBRACE wiredefs vardefs simulation_body_lines RBRACE
    '''

    # The top level of the parser.
    #
    # The output of the parse result is obtained as
    # [  [ module name(string), out_list, in_list, internal_wiredef, internal_vars, lines ], [...], ... ]
    #
    # The name of the main module is ''

    p[0] = [ [ '', p[3], p[2], p[6], p[7], p[8] ] ] + p[4]

def p_const_defs(p):
    '''
    const_defs : 
               | const_def const_defs
    '''
    if len(p) == 3:
        p[0] = p[2] + 1
    else:
        p[0] = 0

def p_const_def(p):
    '''
    const_def : SYM_CONST const_def_list SEMI
    '''
    p[0] = p[2]

def p_const_def_list(p):
    '''
    const_def_list : NAME SYM_EQ NUMBER
                   | NAME SYM_EQ NUMBER COMMA const_def_list
    '''
    dConst[p[1]] = int(p[3])

    if len(p) == 4:
        p[0] = 1
    else:
        p[0] = p[5] + 1

def p_const(p):
    '''
    const : LPAREN const RPAREN
          | const SYM_PLUS  const 
          | const SYM_MINUS const 
          | const SYM_STAR  const 
          | const SYM_SLASH const 
          | NUMBER
          | CONST_REF 
    '''
    if len(p) == 2:
        if p[1].isdigit():
            p[0] = int(p[1])
        else:
            p[0] = dConst[ p[1][1:] ]
    elif p[1] == '(':
        p[0] = [2]
    else:
        if p[2] == '+':
            p[0] = p[1] + p[3]
        if p[2] == '-':
            p[0] = p[1] - p[3]
        if p[2] == '*':
            p[0] = p[1] * p[3]
        if p[2] == '/':
            p[0] = p[1] // p[3]

def p_inputs(p):
    '''
    inputs : input inputs
           | input
    '''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_input(p):
    '''
    input : SYM_INPUT NAME list SEMI
    '''
    # It corresponds to a "input" line
    p[0] = ( (p[2],0,0), p[3])

def p_list(p):
    '''
    list : LBLOCK num_list RBLOCK
    '''
    # It treats lists of numbers such as [0,0,0,0], [0], and [1] ([] is not allowed).
    p[0] = p[2]

def p_num_list(p):
    '''
    num_list : NUMBER
             | NUMBER COMMA num_list
    '''
    # It treats numbers such as "0,0,0,0" and "0" ("" is not allowed).
    if len(p) == 2:
        p[0] = [ int(p[1]) ]
    else:
        p[0] = [ int(p[1]) ] + p[3]

def p_outputs(p):
    '''
    outputs : output outputs
            | output
    '''
    # It treats "output" lines.

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]

def p_output(p):
    '''
    output : SYM_OUTPUT signal_list SEMI
    '''
    # It treats a "output" line.
    p[0] = p[2]


def p_modules(p):
    '''
    modules : 
            | module modules
    '''

    if len(p) < 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_module(p):
    '''
    module : SYM_MODULE NAME LPAREN signal_list RPAREN LPAREN signal_list RPAREN SEMI wiredefs vardefs simulation_body_lines SYM_ENDMODULE
    '''
    #
    # The result of the module definition is parsed as
    # [ module name(string), out_list, in_list, internal_wiredef, internal_vars, lines ]
    #
    out_signals      = p[ 4]
    in_signals       = p[ 7]
    internal_signals = p[10]
    internal_vars    = p[11]
    p[0] = [p[2], out_signals, in_signals, internal_signals, internal_vars, p[12]]

def p_vardefs(p):
    '''
    vardefs : 
            | vardef vardefs
    '''
    if len(p) < 2:
        p[0] = []
    else:
        p[0] = p[1] + p[2]

def p_vardef(p):
    '''
    vardef : SYM_GENVAR name_list SEMI
    '''
    p[0] = p[2]

def p_wiredefs(p):
    '''
    wiredefs : 
             | wiredef wiredefs
    '''
    if len(p) < 2:
        p[0] = []
    else:
        p[0] = p[1] + p[2]

def p_wiredef(p):
    '''
    wiredef : SYM_WIRE signal_list SEMI
    '''

    p[0] = p[2]

def p_signal_list(p):
    '''
    signal_list : signal 
                | signal COMMA signal_list
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_signal(p):
    '''
    signal : NAME 
           | NAME LBLOCK const RBLOCK
           | NAME LBLOCK const COLON const RBLOCK
    '''
    if len(p) == 2:
        p[0] = (p[1],    0,    0)
    elif len(p) == 5:
        p[0] = (p[1], p[3], p[3])
    else:
        p[0] = (p[1], p[3], p[5])


def p_signal_ref_list(p):
    '''
    signal_ref_list : signal_ref
                    | signal_ref COMMA signal_ref_list
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_signal_ref(p):
    '''
    signal_ref : NAME 
               | NAME LBLOCK var_expr RBLOCK
               | NAME LBLOCK var_expr COLON var_expr RBLOCK
    '''
    if len(p) == 2:
        p[0] = (p[1],    0,    0)
    elif len(p) == 5:
        p[0] = (p[1], p[3], p[3])
    else:
        p[0] = (p[1], p[3], p[5])

def p_var_expr(p):
    '''
    var_expr : LPAREN var_expr RPAREN
             | var_expr SYM_PLUS  var_expr 
             | var_expr SYM_MINUS var_expr 
             | var_expr SYM_STAR  var_expr 
             | var_expr SYM_SLASH var_expr 
             | var_expr SYM_EQEQ  var_expr
             | var_expr SYM_NEQ   var_expr
             | var_expr SYM_LT    var_expr
             | var_expr SYM_GT    var_expr
             | NAME SYM_EQ        var_expr
             | NAME SYM_PEQ       var_expr
             | NAME
             | NUMBER
             | CONST_REF
    '''

    if len(p) == 2 :
        if p[1].isdigit():
            p[0] = int(p[1])
        elif p[1][0] == '`':
            p[0] = dConst[ p[1][1:] ]
        else:
            p[0] = p[1]
    elif p[1] == '(':
        p[0] = p[2]
    else:
        lsupported_operator = {'+', '-', '*', '/', '==', '!=', '+=', '<', '>', '='}
        if not( p[2] in lsupported_operator ):
            print('Error: unsupported operator "{}" is used'.format(p[2]), file=sys.stderr)

        p[0] = [ p[2], p[1], p[3]]

def p_name_list(p):
    '''
    name_list : NAME
              | NAME COMMA name_list
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_simulation_body_lines(p):
    '''
    simulation_body_lines : simulation_body_line simulation_body_lines
                          | simulation_body_line
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_simulation_body_line(p):
    '''
    simulation_body_line : gate
                         | moduleInstance
                         | assign
                         | for
    '''
    p[0] = p[1]

def p_assign(p):
    '''
    assign : SYM_ASSIGN signal_ref SYM_EQ signal_ref SEMI
    '''

    def gen_assign(wire_lhs, wire_rhs):
        # print(" appended : assign %s = %s" % (wire_lhs, wire_rhs) )
        return [ 'assign', '', [wire_lhs], [wire_rhs] ]

    p[0] = gen_assign( p[2], p[4] )

def p_for(p):
    '''
    for : SYM_FOR NAME LPAREN var_expr SEMI var_expr SEMI var_expr RPAREN LBRACE for_body_lines RBRACE
    '''

    p[0] = [ 'for', p[2], [p[4], p[6], p[8]], p[11] ]

def p_for_body_lines(p):
    '''
    for_body_lines : for_body_line for_body_lines
                   | for_body_line
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_for_body_line(p):
    '''
    for_body_line : gate
                  | moduleInstance
                  | assign
    '''
    p[0] = p[1]


def p_moduleInstance(p):
    '''
    moduleInstance : signal_ref                    SYM_EQ NAME NAME LPAREN signal_ref_list RPAREN SEMI
                   | LPAREN signal_ref_list RPAREN SYM_EQ NAME NAME LPAREN signal_ref_list RPAREN SEMI
    '''

    def gen_moduleInstance(gate_type, gate_name, gate_output_list, gate_inputs_list):
        # print(" appended : gate_type %s, gate_name %s, gate_output_list %s, gate_inputs_list %s" % (gate_type, gate_name, gate_output_list, gate_inputs_list) )
        return [ gate_type, gate_name, gate_output_list, gate_inputs_list ]

    if len(p) < 10:
        # for a module with a single output
        p[0] = gen_moduleInstance( p[3], p[4], [p[1]], p[6])
    else:
        # for a module with multiple outputs
        p[0] = gen_moduleInstance( p[5], p[6],  p[2] , p[8])


def p_gate(p):
    '''
    gate : signal_ref                    SYM_EQ NAME NAME LPAREN gate_inputs RPAREN SEMI
         | LPAREN signal_ref_list RPAREN SYM_EQ NAME NAME LPAREN gate_inputs RPAREN SEMI
    '''

    def gen_gate(gate_type, gate_name, gate_output_list, gate_inputs_list):
        # print(" appended : gate_type %s, gate_name %s, gate_output_list %s, gate_inputs_list %s" % (gate_type, gate_name, gate_output_list, gate_inputs_list) )
        return [ gate_type, gate_name, gate_output_list, gate_inputs_list ]

    if len(p) == 9:
        # for a gate with a single output
        p[0] = gen_gate( p[3], p[4], [p[1]], p[6])
    else:
        # for a gate with multiple outputs
        p[0] = gen_gate( p[5], p[6],  p[2] , p[8])

def p_gate_inputs(p):
    '''
    gate_inputs : gate_input
                | gate_input COMMA gate_inputs
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        for v in p[3:]:
            p[0] = [p[1]] + v

def p_gate_input(p):
    '''
    gate_input : signal_ref SYM_AT list
               | signal_ref SYM_AT const
    '''
    if isinstance(p[3], list) :
        p[0] = (p[1], p[3])
    else:
        p[0] = (p[1], [ p[3] ] )

def p_error(p):
    print('Syntax error in input! %s' % p, file=sys.stderr)




def check_circuit( circuit_def , debug = False ):
    '''

    Parameters:
    ------------------
        circuit_def : list
            Structure
            [  [ module name(string), out_list, in_list, internal_wiredef, internal_vars, lines ], [...], ... ]
    
    Returns:
    ---------------------
        result : bool
            It resurns True/False when check is passed/not passed.
    '''


    def eval_expr(dVar, arg):

        if isinstance(arg, int):
            return arg

        if isinstance(arg, str):
            return dVar[ arg ]

        if len(arg) == 3:
            arg1 = arg[1]
            arg2 = arg[2]
            if arg[0] == '+':
                return eval_expr(dVar, arg1) + eval_expr(dVar, arg2)
            if arg[0] == '-':
                return eval_expr(dVar, arg1) - eval_expr(dVar, arg2)
            if arg[0] == '*':
                return eval_expr(dVar, arg1) * eval_expr(dVar, arg2)
            if arg[0] == '/':
                return eval_expr(dVar, arg1) // eval_expr(dVar, arg2)
            if arg[0] == '==':
                return 1 if eval_expr(dVar, arg1) == eval_expr(dVar, arg2) else 0
            if arg[0] == '!=':
                return 0 if eval_expr(dVar, arg1) == eval_expr(dVar, arg2) else 1
            if arg[0] == '<':
                return 1 if eval_expr(dVar, arg1) < eval_expr(dVar, arg2) else 0
            if arg[0] == '>':
                return 1 if eval_expr(dVar, arg1) > eval_expr(dVar, arg2) else 0
            if arg[0] == '+=':
                incl = eval_expr(dVar, arg2)
                dVar[ arg1 ] += incl
                return dVar[ arg1 ]
            if arg[0] == '=':
                result = eval_expr(dVar, arg2)
                dVar[ arg1 ] = result
                return result

            print('Error: unknown operator "{}" appears in eval_expr()'.format(arg[0]), file=sys.stderr)

        return 0

    def update_used( lUsed, signal, dVar ):
        start = eval_expr(dVar, signal[1])
        end   = eval_expr(dVar, signal[2])

        for i in range(min(start,end), max(start,end)+1):
            lUsed.append( (signal[0],i) )
        
        return True, abs(start-end) + 1

    def check_lines(dModuleIn, dModuleOut, lines, dVar):

        lUsedInput  = []
        lUsedOutput = []
        sUsedModuleName = set()

        for line in lines:
            gate    = line[0]
            inst    = line[1]
            loutput = line[2]
            linput  = line[3]


            if gate == 'for':
                if inst in sUsedModuleName:
                    print('Error: instance name "{}" is duplicated.'.format(inst))
                    return False, lUsedInput, lUsedOutput

                sUsedModuleName.add( inst )

                result, lusedi, lusedo = check_for(dModuleIn, dModuleOut, line, dVar)

                lUsedInput  += lusedi
                lUsedOutput += lusedo

                if result != True :
                    print('Error: failed in for statement "{}" '.format(inst))
                    return False, lUsedInput, lUsedOutput
            
            elif gate == 'assign':
                resulti, input_width  = update_used(lUsedInput,  linput[0], dVar )
                resulto, output_width = update_used(lUsedOutput, loutput[0], dVar )

                if not(resulti == True and resulto == True and input_width == output_width and input_width == 1):
                    if input_width != output_width:
                        print('Error: bit width is inconsistent in "assign"', file=sys.stderr)
                    if input_width != 1:
                        print('Error: "assign" of multiple bits is not supported currently', file=sys.stderr)
                
                    return False, lUsedInput, lUsedOutput
            else:
                if not(gate in dModuleIn) or not(gate in dModuleOut):
                    print('Error: Unknown module or gate "{}" is used'.format(gate))
                    return False, lUsedInput, lUsedOutput

                if inst in sUsedModuleName:
                    print('Error: instance name "{}" is duplicated.'.format(inst))
                    return False, lUsedInput, lUsedOutput

                sUsedModuleName.add( inst )

                ninput  = len( dModuleIn[gate] )
                noutput = len( dModuleOut[gate] )
                if ninput != len(linput) :
                    print('Error: the number of inputs is not correct in "{}" (instance "{}")'.format(gate, inst))
                    return False, lUsedInput, lUsedOutput
                if noutput != len(loutput) :
                    print('Error: the number of outputs is not correct in "{}" (instance "{}")'.format(gate, inst))
                    return False, lUsedInput, lUsedOutput
                
                for i in range(0, ninput):
                    if len( linput[i] ) == 2 :
                        # gate input xxx@xxx
                        result, width  = update_used(lUsedInput,  linput[i][0], dVar )
                    else:
                        result, width  = update_used(lUsedInput,  linput[i], dVar )

                    if result != True:
                        return False, lUsedInput, lUsedOutput

                    if dModuleIn[gate][i] != width :
                        print('Error: input bit-width is not correct in "{}" (instance "{}")'.format(gate, inst))
                        return False, lUsedInput, lUsedOutput

                for i in range(0, noutput):
                    result, width  = update_used(lUsedOutput,  loutput[i], dVar )

                    if result != True:
                        return False, lUsedInput, lUsedOutput

                    if dModuleOut[gate][i] != width :
                        print('Error: output bit-width is not correct in "{}" (instance "{}")'.format(gate, inst))
                        return False, lUsedInput, lUsedOutput

            

        return True, lUsedInput, lUsedOutput


    def check_for(dModuleIn, dModuleOut, for_body, dVar):
        lUsedInput  = []
        lUsedOutput = []

        gate         = for_body[0]
        inst_name    = for_body[1]
        forCondition = for_body[2]
        lbody        = for_body[3]

        if( not( isinstance(forCondition, list) ) or len(forCondition) != 3 ):
            print('Error: for statement "{}" is not correct'.format(instanceName), file=sys.stderr)
            return False, lUsedInput, lUsedOutput

        eval_expr( dVar, forCondition[0] )
        loop = 0

        while loop < 1000:
            if eval_expr( dVar, forCondition[1] ) == 0:
                return True, lUsedInput, lUsedOutput

            result, lusedi, lusedo = check_lines(dModuleIn, dModuleOut, lbody, dVar)

            lUsedInput  += lusedi
            lUsedOutput += lusedo

            if result != True :
                print('Error: failed in for statement "{}" '.format(inst_name))
                return False, lUsedInput, lUsedOutput

            loop = loop + 1
            eval_expr( dVar, forCondition[2] )

        print('Error: for statement "{}" runs over {} times.'.format(inst_name, loop), file=sys.stderr)

        return False, lUsedInput, lUsedOutput


    def check_module( dModuleIn, dModuleOut, module_def):

        mod_name = mod[0]
        loutputs = mod[1]
        linputs  = mod[2]
        lwires   = mod[3]
        lvars    = mod[4]
        lbody    = mod[5]

        if len(linputs) > 0 and len(linputs[0]) == 2:
            linputs = [ inp for (inp, vect) in mod[2] ]


        dVar = {}
        for var in lvars:
            dVar[ var ] = 0
        
        result, lusedi, lusedo = check_lines(dModuleIn, dModuleOut, lbody, dVar)

        for i in range(0, len(lusedo)):
            if lusedo[i] in lusedo[i+1:]:
                print('Error: "{}" has multiple drivers in module "{}".'.format(lusedo[i], mod_name), file=sys.stderr)
                return False


        defined_wire = []
        for i in range(0, len(lwires)):
            start = eval_expr(dVar, lwires[i][1])
            end   = eval_expr(dVar, lwires[i][2])
            for j in range( min(start, end), max(start, end)+1 ):
                defined_wire.append( (lwires[i][0], j) )
                if not( (lwires[i][0], j) in lusedo ):
                    print('Warning: "{}[{}]" is not driven in module "{}".'.format(lwires[i][0], j, mod_name), file=sys.stderr)
                if not( (lwires[i][0], j) in lusedi ):
                    print('Warning: "{}[{}]" is defined but not used in module "{}".'.format(lwires[i][0], j, mod_name), file=sys.stderr)

        defined_output = []
        for i in range(0, len(loutputs)):
            start = eval_expr(dVar, loutputs[i][1])
            end   = eval_expr(dVar, loutputs[i][2])
            for j in range( min(start, end), max(start, end)+1 ):
                defined_output.append( (loutputs[i][0], j) )
                if not( (loutputs[i][0], j) in lusedo ):
                    print('Error: "{}[{}]" is not driven in module "{}".'.format(loutputs[i][0], j, mod_name), file=sys.stderr)
                    return False

        for outp in lusedo:
            if not( outp in defined_output + defined_wire):
                print('Error: "{}[{}]" is not defined but used as an input in module "{}".'.format(outp[0], outp[1], mod_name), file=sys.stderr)
                return False


        defined_input = []
        for i in range(0, len(linputs)):
            start = eval_expr(dVar, linputs[i][1])
            end   = eval_expr(dVar, linputs[i][2])
            for j in range( min(start, end), max(start, end)+1 ):
                defined_input.append( (linputs[i][0], j) )
                if not( (linputs[i][0], j) in lusedi ):
                    print('Warning: "{}[{}]" is defined but not used in module "{}".'.format(linputs[i][0], j, mod_name), file=sys.stderr)

        for inp in lusedi:
            if not( inp in defined_input + defined_wire ):
                print('Error: "{}[{}]" is not defined but used as an input in module "{}".'.format(inp[0], inp[1], mod_name), file=sys.stderr)
                return False


        if result != True:
            print('Error: occured in module "{}"'.format(mod_name))
            return False

        return True

    if debug :
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( circuit_def )


    dModuleIn  = {}
    dModuleOut = {}
    for mod in circuit_def:
        mod_name = mod[0]
        loutputs = mod[1]
        linputs  = mod[2]

        if mod_name == '':
            continue

        linputWidth = []
        loutputWidth = []

        for i in range(0, len(linputs)):
            start = linputs[i][1]
            end   = linputs[i][2]
            linputWidth.append( abs(start-end) + 1 )

        for i in range(0, len(loutputs)):
            start = loutputs[i][1]
            end   = loutputs[i][2]
            loutputWidth.append( abs(start-end) + 1 )

        dModuleIn[ mod_name  ] = linputWidth
        dModuleOut[ mod_name ] = loutputWidth

    dModuleIn ['NDRO'] = dModuleIn ['ND'] = [1,1,1]
    dModuleOut['NDRO'] = dModuleOut['ND'] = [1]

    dModuleIn ['OR'] = dModuleIn ['XOR'] = dModuleIn ['AND'] = dModuleIn ['RDFF'] = [1,1,1]
    dModuleOut['OR'] = dModuleOut['XOR'] = dModuleOut['AND'] = dModuleOut['RDFF'] = [1]

    dModuleIn ['CB'] = dModuleIn ['D'] = dModuleIn ['NOT'] = [1,1]
    dModuleOut['CB'] = dModuleOut['D'] = dModuleOut['NOT'] = [1]

    dModuleIn ['RTFFB'] = dModuleIn ['T1'] = [1,1]
    dModuleOut['RTFFB'] = dModuleOut['T1'] = [1,1]

    for mod in circuit_def:
        result = check_module( dModuleIn, dModuleOut, mod)
        if result != True:
            return False
    
    return True

def parse_and_execute( data, debug = False ):
    parser = yacc.yacc()

    global dConst
    dConst = {}
    result = parser.parse(data, debug = debug)

    if( check_circuit( result, debug = debug ) ):
        sfqsim_gates.exec_simulation( result, debug = debug )




if __name__ == '__main__':
    param = sys.argv

    if len(param) == 2 :
        file = open(param[1], 'rt')
        source_input = file.read()
        file.close()
    else :
        source_input = sys.stdin.read()

        parse_and_execute( source_input )

