# -*- encoding: utf-8 -*-

import sys

dGateLatch = {}
dSignal = {}
dVar    = {}

LOGIC_VAL_UNKNOWN = -1
LOGIC_VAL_ERROR   = -2


def resetLogicSim():
    global dGateLatch
    global dSignal
    global dVar

    dGateLatch = {}
    dSignal = {}
    dVar    = {}

def gRDFF(cycle, instStr, set_tuple, rst_tuple, clk_tuple):
    (set_vect, set_ord)  =  set_tuple
    (rst_vect, rst_ord)  =  rst_tuple
    (clk_vect, clk_ord)  =  clk_tuple

    
    if instStr in dGateLatch:
        state = dGateLatch[instStr]
    else:
        state = 0

    
    ordlist = list(set(set_ord + rst_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        set_val = set_vect[cycle][set_ord.index(o)] if (o in set_ord) else 0
        rst_val = rst_vect[cycle][rst_ord.index(o)] if (o in rst_ord) else 0
        clk_val = clk_vect[cycle][clk_ord.index(o)] if (o in clk_ord) else 0

        if (set_val==1 and rst_val==1) or ((set_val==1 or rst_val==1) and clk_val==1):
            state = LOGIC_VAL_ERROR

        if set_val == LOGIC_VAL_ERROR or rst_val == LOGIC_VAL_ERROR or clk_val == LOGIC_VAL_ERROR:
            state = LOGIC_VAL_ERROR
        if state != LOGIC_VAL_ERROR:
            if set_val == LOGIC_VAL_UNKNOWN or rst_val == LOGIC_VAL_UNKNOWN or clk_val == LOGIC_VAL_UNKNOWN:
                state = LOGIC_VAL_UNKNOWN
                
        if not(state == LOGIC_VAL_ERROR or state == LOGIC_VAL_UNKNOWN):
            if set_val == 1:
                if state == 1:
                    state = LOGIC_VAL_ERROR
                else:
                    state = 1
            if rst_val == 1:
                state = 0
        
        if clk_val == 1:
            val.append(state)
            if state == 0 or state == 1:
                state = 0

    if len(val) == 0:
        val.append(0)

    dGateLatch[instStr] = state

    return val

def gRTFFB(cycle, instStr, rst_tuple, clk_tuple):
    (rst_vect, rst_ord)  =  rst_tuple
    (clk_vect, clk_ord)  =  clk_tuple

    
    if instStr in dGateLatch:
        state = dGateLatch[instStr]
    else:
        state = 0

    
    ordlist = list(set(rst_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        rst_val = rst_vect[cycle][rst_ord.index(o)] if (o in rst_ord) else 0
        clk_val = clk_vect[cycle][clk_ord.index(o)] if (o in clk_ord) else 0

        if (rst_val==1 and clk_val==1) or rst_val == LOGIC_VAL_ERROR or clk_val == LOGIC_VAL_ERROR:
            state = LOGIC_VAL_ERROR

        if state != LOGIC_VAL_ERROR:
            if rst_val == LOGIC_VAL_UNKNOWN or clk_val == LOGIC_VAL_UNKNOWN:
                state = LOGIC_VAL_UNKNOWN
                
        if not(state == LOGIC_VAL_ERROR or state == LOGIC_VAL_UNKNOWN):
            if rst_val == 1:
                state = 0
        
        if clk_val == 1:
            val.append([1-state])
            val.append([state])
            if state == 0:
                state = 1
            elif state == 1:
                state = 0

    if len(val) == 0:
        val.append([0])
        val.append([0])

    dGateLatch[instStr] = state

    return val

def gT1(cycle, instStr, data_tuple, clk_tuple):
    (data_vect, data_ord)  =  data_tuple
    (clk_vect, clk_ord)    =  clk_tuple

    
    if instStr in dGateLatch:
        state = dGateLatch[instStr]
    else:
        state = 0

    
    ordlist = list(set(data_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        dat_val = data_vect[cycle][data_ord.index(o)] if (o in data_ord) else 0
        clk_val = clk_vect [cycle][clk_ord .index(o)] if (o in clk_ord ) else 0

        if (dat_val==1 and clk_val==1) or dat_val == LOGIC_VAL_ERROR or clk_val == LOGIC_VAL_ERROR:
            state = LOGIC_VAL_ERROR

        if state != LOGIC_VAL_ERROR:
            if dat_val == LOGIC_VAL_UNKNOWN or clk_val == LOGIC_VAL_UNKNOWN:
                state = LOGIC_VAL_UNKNOWN
                

        if clk_val == 1:
            val.append([state])
            val.append([0])
            if state == 0 or state == 1:
                state = 0
        elif dat_val == 1:
            val.append([0])
            val.append([state])
            if state == 0 or state == 1:
                state = 1 - state


    if len(val) == 0:
        val.append([0])
        val.append([0])

    dGateLatch[instStr] = state

    return val    
    
def gCB(cycle, instStr, in0_tuple, in1_tuple):
    (in0_vect, in0_ord)  =  in0_tuple
    (in1_vect, in1_ord)  =  in1_tuple
    
    ordlist = list(set(in0_ord + in1_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        ord_count = 0

        for idx in range(0, len(in0_ord)):
            if o == in0_ord[idx] :
                if ord_count == LOGIC_VAL_ERROR or ord_count == LOGIC_VAL_UNKNOWN:
                    break
                elif in0_vect[cycle][idx] >= 0:
                    ord_count = ord_count + in0_vect[cycle][idx]

        for idx in range(0, len(in1_ord)):
            if o == in1_ord[idx] :
                if ord_count == LOGIC_VAL_ERROR or ord_count == LOGIC_VAL_UNKNOWN:
                    break
                elif o == in1_ord[idx] :
                    ord_count = ord_count + in1_vect[cycle][idx]

        if ord_count >= 2 :
            ord_count = LOGIC_VAL_ERROR
            
        val.append(ord_count)

    return val


def gD_gNOT(cycle, instStr, in_tuple, clk_tuple, bool_output_negate):

    ( in_vect,  in_ord)  =  in_tuple
    (clk_vect, clk_ord)  =  clk_tuple
    
    if instStr in dGateLatch:
        in_latch = dGateLatch[instStr]
    else:
        in_latch = LOGIC_VAL_UNKNOWN

    
    ordlist = list(set(in_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        if o in in_ord:
            if in_latch == LOGIC_VAL_ERROR:
                in_latch = LOGIC_VAL_ERROR
            elif in_latch == LOGIC_VAL_UNKNOWN:
                in_latch = LOGIC_VAL_UNKNOWN
            elif len(in_vect) <= cycle:
                if cycle == 0:
                    in_latch = LOGIC_VAL_UNKNOWN
                elif in_latch + in_vect[cycle-1][in_ord.index(o)] >= 2:
                    in_latch = LOGIC_VAL_ERROR
                else:
                    in_latch = in_latch + in_vect[cycle-1][in_ord.index(o)]
            elif in_latch + in_vect[cycle][in_ord.index(o)] >= 2:
                in_latch = LOGIC_VAL_ERROR
            else:
                in_latch = in_latch + in_vect[cycle][in_ord.index(o)]
                
        if o in clk_ord:
            if clk_vect[cycle][clk_ord.index(o)] == 1:
                if in_latch == 1:
                    if bool_output_negate:
                        val.append( 0 )
                    else:
                        val.append( 1 )
                    in_latch = 0
                elif in_latch == LOGIC_VAL_ERROR:
                    val.append( LOGIC_VAL_ERROR )
                    in_latch = LOGIC_VAL_ERROR
                elif in_latch == 0:
                    if bool_output_negate:
                        val.append( 1 )
                    else:
                        val.append( 0 )
                    in_latch = 0
                else:
                    val.append( LOGIC_VAL_UNKNOWN )
                    in_latch = 0

            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                val.append( LOGIC_VAL_UNKNOWN )
                in_latch = LOGIC_VAL_UNKNOWN
                
            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_ERROR:
                val.append( LOGIC_VAL_ERROR )
                in_latch = LOGIC_VAL_ERROR

    dGateLatch[instStr] = in_latch

    return val


def gNDRO(cycle, instStr, rst_tuple, set_tuple, clk_tuple):

    (rst_vect, rst_ord)  =  rst_tuple
    (set_vect, set_ord)  =  set_tuple
    (clk_vect, clk_ord)  =  clk_tuple
    
    if instStr in dGateLatch:
        latch = dGateLatch[instStr]
    else:
        latch = 0

    ordlist = list(set(rst_ord + set_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        if o in rst_ord:
            if len(rst_vect) <= cycle:
                if cycle == 0:
                    latch = latch
                elif rst_vect[cycle-1][rst_ord.index(o)] == 1:
                    latch = 0
                elif rst_vect[cycle-1][rst_ord.index(o)] == LOGIC_VAL_ERROR:
                    latch = LOGIC_VAL_ERROR
                elif rst_vect[cycle-1][rst_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                    latch = LOGIC_VAL_UNKNOWN
            else:
                if rst_vect[cycle][rst_ord.index(o)] == 1:
                    latch = 0
                elif rst_vect[cycle][rst_ord.index(o)] == LOGIC_VAL_ERROR:
                    latch = LOGIC_VAL_ERROR
                elif rst_vect[cycle][rst_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                    latch = LOGIC_VAL_UNKNOWN
                
        if o in set_ord:
            if latch == LOGIC_VAL_ERROR:
                latch = LOGIC_VAL_ERROR
            elif latch == LOGIC_VAL_UNKNOWN:
                latch = LOGIC_VAL_UNKNOWN
            else:
                if set_vect[cycle][set_ord.index(o)] == 1:
                    latch = 1
                elif set_vect[cycle][set_ord.index(o)] == LOGIC_VAL_ERROR:
                    latch = LOGIC_VAL_ERROR
                elif set_vect[cycle][set_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                    latch = LOGIC_VAL_UNKNOWN

        if o in clk_ord:
            if clk_vect[cycle][clk_ord.index(o)] == 1:
                if latch == 1:
                    val.append( 1 )
                elif latch == LOGIC_VAL_ERROR:
                    val.append( LOGIC_VAL_ERROR )
                elif latch == 0:
                    val.append( 0 )
                else:
                    val.append( LOGIC_VAL_UNKNOWN )

            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                val.append( LOGIC_VAL_UNKNOWN )
                latch = LOGIC_VAL_UNKNOWN
                    
            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_ERROR:
                val.append( LOGIC_VAL_ERROR )
                latch = LOGIC_VAL_ERROR
            else:
                val.append( 0 )

    dGateLatch[instStr] = latch

    return val

def gXOR(cycle, instStr, in0_tuple, in1_tuple, clk_tuple):

    (in0_vect, in0_ord)  =  in0_tuple
    (in1_vect, in1_ord)  =  in1_tuple
    (clk_vect, clk_ord)  =  clk_tuple
    
    if instStr in dGateLatch:
        (in0_latch, in1_latch) = dGateLatch[instStr]
    else:
        in0_latch = in1_latch = 0

    
    ordlist = list(set(in0_ord + in1_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        if o in in0_ord:
            if in0_latch == LOGIC_VAL_ERROR:
                in0_latch = LOGIC_VAL_ERROR
            elif in0_latch == LOGIC_VAL_UNKNOWN:
                in0_latch = LOGIC_VAL_UNKNOWN
            elif len(in0_vect) <= cycle:
                if cycle == 0:
                    in0_latch = LOGIC_VAL_UNKNOWN
                elif in0_latch + in0_vect[cycle-1][in0_ord.index(o)] >= 2:
                    in0_latch = LOGIC_VAL_ERROR
                else:
                    in0_latch = in0_latch + in0_vect[cycle-1][in0_ord.index(o)]
            elif in0_latch + in0_vect[cycle][in0_ord.index(o)] >= 2:
                in0_latch = LOGIC_VAL_ERROR
            else:
                in0_latch = in0_latch + in0_vect[cycle][in0_ord.index(o)]
                
        if o in in1_ord:
            if in1_latch == LOGIC_VAL_ERROR:
                in1_latch = LOGIC_VAL_ERROR
            elif in1_latch == LOGIC_VAL_UNKNOWN:
                in1_latch = LOGIC_VAL_UNKNOWN
            elif len(in1_vect) <= cycle:
                if cycle == 0:
                    in1_latch = LOGIC_VAL_UNKNOWN
                elif in1_latch + in1_vect[cycle-1][in1_ord.index(o)] >= 2:
                    in1_latch = LOGIC_VAL_ERROR
                else:
                    in1_latch = in1_latch + in1_vect[cycle-1][in1_ord.index(o)]
            elif in1_latch + in1_vect[cycle][in1_ord.index(o)] >= 2:
                in1_latch = LOGIC_VAL_ERROR
            else:
                in1_latch = in1_latch + in1_vect[cycle][in1_ord.index(o)]

        if o in clk_ord:
            if clk_vect[cycle][clk_ord.index(o)] == 1:
                if (in0_latch == 1 and in1_latch == 0) or (in0_latch == 0 and in1_latch == 1):
                    val.append( 1 )
                    in0_latch = 0
                    in1_latch = 0
                elif in0_latch == LOGIC_VAL_ERROR or in1_latch == LOGIC_VAL_ERROR :
                    val.append( LOGIC_VAL_ERROR )
                    in0_latch = LOGIC_VAL_ERROR
                    in1_latch = LOGIC_VAL_ERROR
                elif (in0_latch == 0 and in1_latch == 0) or (in0_latch == 1 and in1_latch == 1):
                    val.append( 0 )
                    in0_latch = 0
                    in1_latch = 0
                else:
                    val.append( LOGIC_VAL_UNKNOWN )
                    in0_latch = 0
                    in1_latch = 0

            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                val.append( LOGIC_VAL_UNKNOWN )
                in0_latch = LOGIC_VAL_UNKNOWN
                in1_latch = LOGIC_VAL_UNKNOWN
                    
            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_ERROR:
                val.append( LOGIC_VAL_ERROR )
                in0_latch = LOGIC_VAL_ERROR
                in1_latch = LOGIC_VAL_ERROR

    dGateLatch[instStr] = (in0_latch, in1_latch)

    return val

def gOR(cycle, instStr, in0_tuple, in1_tuple, clk_tuple):

    (in0_vect, in0_ord)  =  in0_tuple
    (in1_vect, in1_ord)  =  in1_tuple
    (clk_vect, clk_ord)  =  clk_tuple
    
    if instStr in dGateLatch:
        (in0_latch, in1_latch) = dGateLatch[instStr]
    else:
        in0_latch = in1_latch = 0

    
    ordlist = list(set(in0_ord + in1_ord + clk_ord))
    ordlist.sort()
    
    val = []
    for o in ordlist:
        if o in in0_ord:
            if in0_latch == LOGIC_VAL_ERROR:
                in0_latch = LOGIC_VAL_ERROR
            elif in0_latch == LOGIC_VAL_UNKNOWN:
                in0_latch = LOGIC_VAL_UNKNOWN
            elif len(in0_vect) <= cycle:
                if cycle == 0:
                    in0_latch = LOGIC_VAL_UNKNOWN
                elif in0_latch + in0_vect[cycle-1][in0_ord.index(o)] >= 2:
                    in0_latch = LOGIC_VAL_ERROR
                else:
                    in0_latch = in0_latch + in0_vect[cycle-1][in0_ord.index(o)]
            elif in0_latch + in0_vect[cycle][in0_ord.index(o)] >= 2:
                in0_latch = LOGIC_VAL_ERROR
            else:
                in0_latch = in0_latch + in0_vect[cycle][in0_ord.index(o)]
                    
        if o in in1_ord:
            if in1_latch == LOGIC_VAL_ERROR:
                in1_latch = LOGIC_VAL_ERROR
            elif in1_latch == LOGIC_VAL_UNKNOWN:
                in1_latch = LOGIC_VAL_UNKNOWN
            elif len(in1_vect) <= cycle:
                if cycle == 0:
                    in1_latch = LOGIC_VAL_UNKNOWN
                elif in1_latch + in1_vect[cycle-1][in1_ord.index(o)] >= 2:
                    in1_latch = LOGIC_VAL_ERROR
                else:
                    in1_latch = in1_latch + in1_vect[cycle-1][in1_ord.index(o)]
            elif in1_latch + in1_vect[cycle][in1_ord.index(o)] >= 2:
                in1_latch = LOGIC_VAL_ERROR
            else:
                in1_latch = in1_latch + in1_vect[cycle][in1_ord.index(o)]

        if o in clk_ord:
            if clk_vect[cycle][clk_ord.index(o)] == 1:
                if (in0_latch == 1 and in1_latch == 0) or (in0_latch == 0 and in1_latch == 1) or (in0_latch == 1 and in1_latch == 1) :
                    val.append( 1 )
                    in0_latch = 0
                    in1_latch = 0
                elif in0_latch == LOGIC_VAL_ERROR or in1_latch == LOGIC_VAL_ERROR :
                    val.append( LOGIC_VAL_ERROR )
                    in0_latch = LOGIC_VAL_ERROR
                    in1_latch = LOGIC_VAL_ERROR
                elif in0_latch == 0 and in1_latch == 0 :
                    val.append( 0 )
                    in0_latch = 0
                    in1_latch = 0
                else:
                    val.append( LOGIC_VAL_UNKNOWN )
                    in0_latch = 0
                    in1_latch = 0

            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                val.append( LOGIC_VAL_UNKNOWN )
                in0_latch = LOGIC_VAL_UNKNOWN
                in1_latch = LOGIC_VAL_UNKNOWN
                    
            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_ERROR:
                val.append( LOGIC_VAL_ERROR )
                in0_latch = LOGIC_VAL_ERROR
                in1_latch = LOGIC_VAL_ERROR

    dGateLatch[instStr] = (in0_latch, in1_latch)

    return val


def gAND(cycle, instStr, in0_tuple, in1_tuple, clk_tuple):

    (in0_vect, in0_ord)  =  in0_tuple
    (in1_vect, in1_ord)  =  in1_tuple
    (clk_vect, clk_ord)  =  clk_tuple
    
    if instStr in dGateLatch:
        (in0_latch, in1_latch) = dGateLatch[instStr]
    else:
        in0_latch = in1_latch = 0

    
    ordlist = list(set(in0_ord + in1_ord + clk_ord))
    ordlist.sort()

    val = []
    #for ordlist_idx in range(0,len(ordlist)):
    #    o = ordlist[ordlist_idx]
    for o in ordlist:
        if o in in0_ord:
            if in0_latch == LOGIC_VAL_ERROR:
                in0_latch = LOGIC_VAL_ERROR
            elif in0_latch == LOGIC_VAL_UNKNOWN:
                in0_latch = LOGIC_VAL_UNKNOWN
            elif len(in0_vect) <= cycle:
                if cycle == 0:
                    in0_latch = LOGIC_VAL_UNKNOWN
                elif in0_latch + in0_vect[cycle-1][in0_ord.index(o)] >= 2:
                    in0_latch = LOGIC_VAL_ERROR
                else:
                    in0_latch = in0_latch + in0_vect[cycle-1][in0_ord.index(o)]
            elif in0_latch + in0_vect[cycle][in0_ord.index(o)] >= 2:
                in0_latch = LOGIC_VAL_ERROR
            else:
                in0_latch = in0_latch + in0_vect[cycle][in0_ord.index(o)]
                    
        if o in in1_ord:
            if in1_latch == LOGIC_VAL_ERROR:
                in1_latch = LOGIC_VAL_ERROR
            elif in1_latch == LOGIC_VAL_UNKNOWN:
                in1_latch = LOGIC_VAL_UNKNOWN
            elif len(in1_vect) <= cycle:
                if cycle == 0:
                    in1_latch = LOGIC_VAL_UNKNOWN
                elif in1_latch + in1_vect[cycle-1][in1_ord.index(o)] >= 2:
                    in1_latch = LOGIC_VAL_ERROR
                else:
                    in1_latch = in1_latch + in1_vect[cycle-1][in1_ord.index(o)]
            elif in1_latch + in1_vect[cycle][in1_ord.index(o)] >= 2:
                in1_latch = LOGIC_VAL_ERROR
            else:
                in1_latch = in1_latch + in1_vect[cycle][in1_ord.index(o)]

        if o in clk_ord:
            if clk_vect[cycle][clk_ord.index(o)] == 1:
                if in0_latch == 1 and in1_latch == 1 :
                    val.append( 1 )
                    in0_latch = 0
                    in1_latch = 0
                elif in0_latch == LOGIC_VAL_ERROR or in1_latch == LOGIC_VAL_ERROR :
                    val.append( LOGIC_VAL_ERROR )
                    in0_latch = LOGIC_VAL_ERROR
                    in1_latch = LOGIC_VAL_ERROR
                elif in0_latch == 0 or in1_latch == 0 :
                    val.append( 0 )
                    in0_latch = 0
                    in1_latch = 0
                else:
                    val.append( LOGIC_VAL_UNKNOWN )
                    in0_latch = 0
                    in1_latch = 0

            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_UNKNOWN:
                val.append( LOGIC_VAL_UNKNOWN )
                in0_latch = LOGIC_VAL_UNKNOWN
                in1_latch = LOGIC_VAL_UNKNOWN
                    
            elif clk_vect[cycle][clk_ord.index(o)] == LOGIC_VAL_ERROR:
                val.append( LOGIC_VAL_ERROR )
                in0_latch = LOGIC_VAL_ERROR
                in1_latch = LOGIC_VAL_ERROR

    dGateLatch[instStr] = (in0_latch, in1_latch)

    return val


def find_module_def(moduleStr, circuit_def):
    '''
    when it find a module definition specified by "moduleStr",
    it returns the module definition
    '''

    result = []
    for mod in circuit_def:
        mod_name = mod[0]

        if mod_name == moduleStr:
            result = mod
            break
   
    return result


def getSignal( prefix, sig ):
    '''
    It retuens a list of values corresponding to "sig"
    '''
    global dSignal

    (arg_name, arg_bus_start, arg_bus_end) = sig

    bus_start = eval_var_expr(prefix, arg_bus_start)
    bus_end   = eval_var_expr(prefix, arg_bus_end)

    if bus_start == bus_end:
        arg = dSignal[(prefix + arg_name, bus_start)]
    else:
        print('Internal Error: signal "{}" is assumed to be 1-bit signal'.format(arg_name), file=sys.stderr)
        arg = []

    return arg

def getSignalsWithName( prefix, sig ):
    '''
    It returns a list of tuples of a 1-bit signal name and its values corresponding to "sig"
    '''
    global dSignal

    (arg_name, arg_bus_start, arg_bus_end) = sig

    bus_start = eval_var_expr(prefix, arg_bus_start)
    bus_end   = eval_var_expr(prefix, arg_bus_end)

    result = []

    if bus_start == bus_end and bus_start == 0 :
        result.append( (prefix + arg_name, dSignal[(prefix + arg_name, 0)]) )
    elif bus_start <= bus_end :
        for i in range(bus_start, bus_end+1, +1):
            result.append( (prefix + arg_name+'[{}]'.format(i), dSignal[(prefix + arg_name, i)]) )
    else:
        for i in range(bus_start, bus_end-1, -1):
            result.append( (prefix + arg_name+'[{}]'.format(i), dSignal[(prefix + arg_name, i)]) )

    return result

def getSignals( prefix, sig ):
    '''
    It returns a list of vectors in the bus corresponding to "sig"
    '''

    return [ v for ( _, v) in getSignalsWithName(prefix, sig) ]


def setSignal( prefix, sig, lval ):
    '''
    It sets a list of values corresponding to "sig"
    '''

    global dSignal

    (arg_name, arg_bus_start, arg_bus_end) = sig

    bus_start = eval_var_expr(prefix, arg_bus_start)
    bus_end   = eval_var_expr(prefix, arg_bus_end)

    if bus_start == bus_end:
        dSignal[(prefix + arg_name, bus_start)] = lval
    else:
        print('Internal Error: signal "{}" is assumed to be 1-bit signal'.format(arg_name), file=sys.stderr)


def eval_var_expr(prefix, arg):

    if isinstance(arg, int):
        return arg

    if isinstance(arg, str):
        return dVar[ prefix + arg ]

    if len(arg) == 3:
        arg0 = arg[0]
        arg1 = arg[1]
        arg2 = arg[2]

        if arg0 == '+': 
            return eval_var_expr(prefix, arg1) + eval_var_expr(prefix, arg2)
        if arg0 == '-':
            return eval_var_expr(prefix, arg1) - eval_var_expr(prefix, arg2)
        if arg0 == '*':
            return eval_var_expr(prefix, arg1) * eval_var_expr(prefix, arg2)
        if arg0 == '/':
            return eval_var_expr(prefix, arg1) // eval_var_expr(prefix, arg2)
        if arg0 == '>':
            return 1 if eval_var_expr(prefix, arg1) > eval_var_expr(prefix, arg2) else 0
        if arg0 == '<':
            return 1 if eval_var_expr(prefix, arg1) < eval_var_expr(prefix, arg2) else 0
        if arg0 == '==':
            return 1 if eval_var_expr(prefix, arg1) == eval_var_expr(prefix, arg2) else 0
        if arg0 == '!=':
            return 1 if eval_var_expr(prefix, arg1) != eval_var_expr(prefix, arg2) else 0
        if arg0 == '+=':
            incl = eval_var_expr(prefix, arg2)
            dVar[ prefix + arg1 ] += incl
            return dVar[ prefix + arg1 ]
        if arg0 == '=':
            result = eval_var_expr(prefix, arg2)
            dVar[ prefix + arg1 ] = result
            return result

        print('Error: unsupported operation "{}"'.format(arg0))
        return 0

    print('Error: unsupported expression "{}"'.format( str(arg) ) )

    return 0


def exec_lines(instancePrefix, instanceSuffix, lbody, cycle, circuit_def):
    '''
    It executes lines sequentially.
    Lines should be reordered to be execute correctly according to dependency of data.

    Parameters:
    ---------------------
        instancePrefix : str
            prefix of instance name. it must contain '.' at last or it must be ''
        instanceSuffix : str
            suffix of instance name
        lbody : list
            it is a list of lines
        circuit_def : list
            it is a complete list of module definitions.
            It is used to instantiate modules.
    Returns:
    ---------------------
        result : bool
            Whether the execution of lines is succeeded
    '''

    for line in lbody:
        line_gate = line[0]
        line_inst = line[1]
        line_loutput= line[2]
        line_linput = line[3]

        combined_inst_name = line_inst + instanceSuffix

        if( line_gate == 'D' or line_gate == 'NOT' or line_gate == 'CB'):
            # syntax check
            if len(line_linput) != 2:
                print('Error: number of input pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False
            if len(line_loutput) != 1:
                print('Error: number of output pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False

            arg0_bus, arg0_ord = line_linput[0]
            arg1_bus, arg1_ord = line_linput[1]

            arg0 = getSignal(instancePrefix, arg0_bus)
            arg1 = getSignal(instancePrefix, arg1_bus)

            if line_gate == 'D':
                result = gD_gNOT(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), False )
            elif line_gate == 'NOT':
                result = gD_gNOT(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), True )
            elif line_gate == 'CB':
                result = gCB    (cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord))
            else:
                print('Error: unknown gate "{}" (instance "{}")'.format(line_gate, instancePrefix + combined_inst_name), file=sys.stderr)
                return False

            getSignal( instancePrefix, line_loutput[0] ) . append( result )

        elif( line_gate == 'AND' or line_gate == 'OR' or line_gate == 'XOR' or line_gate == 'ND' or line_gate == 'NDRO' or line_gate == 'RDFF' ):
            # syntax check
            if len(line_linput) != 3:
                print('Error: number of input pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False
            if len(line_loutput) != 1:
                print('Error: number of output pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False

            arg0_bus, arg0_ord = line_linput[0]
            arg1_bus, arg1_ord = line_linput[1]
            arg2_bus, arg2_ord = line_linput[2]

            arg0 = getSignal(instancePrefix, arg0_bus)
            arg1 = getSignal(instancePrefix, arg1_bus)
            arg2 = getSignal(instancePrefix, arg2_bus)

            if line_gate == 'AND':
                result =  gAND(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), (arg2, arg2_ord))
            elif line_gate == 'OR':
                result =  gOR (cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), (arg2, arg2_ord))
            elif line_gate == 'XOR':
                result =  gXOR(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), (arg2, arg2_ord))
            elif line_gate == 'ND' or line_gate == 'NDRO':
                result = gNDRO(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), (arg2, arg2_ord))
            elif line_gate == 'RDFF':
                result = gRDFF(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord), (arg2, arg2_ord))
            else:
                print('Error: unknown gate "{}" (instance "{}")'.format(line_gate, instancePrefix + combined_inst_name), file=sys.stderr)
                return False

            getSignal( instancePrefix, line_loutput[0] ).append( result )

        elif( line_gate == 'RTFFB' or line_gate == 'T1' ):
            # syntax check
            if len(line_linput) != 2:
                print('Error: number of input pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False
            if len(line_loutput) != 2:
                print('Error: number of output pins are not consistent for "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False

            arg0_bus, arg0_ord = line_linput[0]
            arg1_bus, arg1_ord = line_linput[1]

            arg0 = getSignal(instancePrefix, arg0_bus)
            arg1 = getSignal(instancePrefix, arg1_bus)

            if line_gate == 'RTFFB':
                result =  gRTFFB(cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord))
            elif line_gate == 'T1':
                result =  gT1(   cycle, instancePrefix + combined_inst_name, (arg0, arg0_ord), (arg1, arg1_ord))
            else:
                print('Error: unknown gate "{}" (instance "{}")'.format(line_gate, instancePrefix + combined_inst_name), file=sys.stderr)
                return False

            getSignal( instancePrefix, line_loutput[0] ).append( result[0] )
            getSignal( instancePrefix, line_loutput[1] ).append( result[1] )

        elif( line_gate == 'assign' ):
            getSignal( instancePrefix, line_loutput[0] ).append( getSignal( instancePrefix, line_linput[0] )[cycle] )

        elif( line_gate == 'for' ):
            exec_for(instancePrefix, instanceSuffix, combined_inst_name, line_loutput, line_linput, cycle, circuit_def)

        elif( len(line_linput) > 0 and (type( (line_linput[0])[0] ) is str) ):
            # call module

            call_module = find_module_def(line_gate, circuit_def)
            # it returns the module definition [ module name, out_name_list, in_name_list, ... ]

            if call_module == []:
                print('Error: cannot find out module "{}"'.format(line_gate), file=sys.stderr)
                return False

            call_module_linput  = call_module[2]
            call_module_loutput = call_module[1]

            # syntax check
            if len(line_linput) != len(call_module_linput) :
                print('Error: number of input pins are not consistent for module "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False
            if len(line_loutput) != len(call_module_loutput) :
                print('Error: number of output pins are not consistent for module "{}" (instance "{}")'.format(line_gate, combined_inst_name), file=sys.stderr)
                return False

            # set module inputs
            for call_module_input_idx in range(0, len(call_module_linput)):
                # TODO : bit width of each module inputs should be 1
                call_module_input = call_module_linput[call_module_input_idx]
                caller_arg_value  = getSignal(instancePrefix, line_linput[ call_module_input_idx ])

                if cycle == 0 :
                    setSignal(instancePrefix + combined_inst_name + '.', call_module_input, [ caller_arg_value[cycle] ] )
                else:
                    getSignal(instancePrefix + combined_inst_name + '.', call_module_input).append( caller_arg_value[cycle] )

            # execute module
            result = exec_module(instancePrefix + combined_inst_name, '', line_gate, cycle, circuit_def)
            if result == False:
                return False

            # set module outputs
            for call_module_output_idx in range(0, len(call_module_loutput)):
                # TODO : bit width of each module outputs should be 1

                call_module_output = call_module_loutput[call_module_output_idx]
                call_result_value = getSignal(instancePrefix + combined_inst_name + '.', call_module_output)[cycle]
                getSignal(instancePrefix, line_loutput[ call_module_output_idx ]).append( call_result_value )

        else:
            print('Error: unknown gate/module "{}" appears in module "{}"'.format(line_gate, mod_name), file=sys.stderr)
            return False

def exec_for(instancePrefix, instanceSuffix, instanceName, forCondition, forBody, cycle, circuit_def):

    if( not( isinstance(forCondition, list) ) or len(forCondition) != 3 ):
        print('Error: for statement "{}" is not correct'.format(instanceName), file=sys.stderr)
        return False

    eval_var_expr( instancePrefix, forCondition[0] )
    loop = 0

    while loop < 1000:
        if eval_var_expr( instancePrefix, forCondition[1] ) == 0:
            return True

        suffix = '_' + instanceName + '_loop={}'.format(loop)
        exec_lines(instancePrefix, instanceSuffix + suffix , forBody, cycle, circuit_def)

        loop = loop + 1
        eval_var_expr( instancePrefix, forCondition[2] )

    print('Error: for statement "{}" runs over {} times.'.format(instanceName, loop), file=sys.stderr)

    return False

def exec_module(instancePath, instanceSuffix, moduleStr, cycle, circuit_def):
    # Structure of circuit_def:
    # [  [ module name, out_name_list, in_name_list, internal_wiredef, internal_vars, lines ], [...], ... ]

    linputs  = circuit_def[0][2]
    lbody    = circuit_def[0][4]

    global dSignal
    global dVar

    if instancePath == '':
        instancePrefix = ''

        for inp in linputs:
            ((name, v_start, v_end), vect) = inp
            if v_start != 0 or v_end != 0:
                print('Internal Error: circuit input "{}" is assumed to be 1-bit signal'.format(name), file=sys.stderr)
            
            if cycle == 0:
                dSignal[ (instancePrefix + name, 0)] = [ vect[0] ]
            else:
                dSignal[ (instancePrefix + name, 0)].append( vect[cycle] )
    else:
        instancePrefix = instancePath + '.'

    module = find_module_def(moduleStr, circuit_def)
    if module == []:
        print('Error: unknown module "{}" appears'.format(moduleStr), file=sys.stderr)
        return False

    mod_name = module[0]
    loutputs = module[1]
    linputs  = module[2]
    lwires   = module[3]
    lvars    = module[4]
    lbody    = module[5]

    if cycle == 0 :
        for (sig, v_start, v_end) in loutputs + lwires:
            for i in range(min(v_start,v_end), max(v_start,v_end)+1):
                dSignal[ (instancePrefix + sig, i) ] = []

    exec_lines(instancePrefix, instanceSuffix, lbody, cycle, circuit_def)





def exec_simulation( circuit_def, debug = False ):
    # Structure of circuit_def:
    # [  [ module name(string), out_list, in_list, internal_wiredef, internal_vars, lines ], [...], ... ]

    resetLogicSim()
 
    linputs  = circuit_def[0][2]
    loutputs = circuit_def[0][1]
#    lwires   = circuit_def[0][3]
#    lbody    = circuit_def[0][4]

    ncycle = len( (linputs[0])[1] )

    for inp in linputs:
        ( (in_string, _, _), vect) = inp
        for i in range(0, len(vect)):
            vect[i] = [ vect[i] ]
        if( ncycle != len(vect) ):
            print('Warning: vector length for input "{}" is not consistent'.format(in_string), file=sys.stderr)
        ncycle = min( ncycle, len(vect) )

    print('Info: execute {} cycles'.format(ncycle))

    for cycle in range(0, ncycle):
        if False == exec_module('', '', '', cycle, circuit_def):
            break

    if debug:
        print( dSignal )

    linputname=[]
    for inp in linputs:
        ( (in_string, _, _), vect) = inp
        linputname.append(in_string)

    loutputname=[]
    for outp in loutputs:
        (out_string, _, _) = outp
        loutputname.append(out_string)


    def vect_to_str( vect ):
        result = ''
        firstnum = True
        for i in vect:
            if firstnum == False:
                result += ', '
            else:
                firstnum = False

            if isinstance(i, list):
                stri = '[' + vect_to_str(i) + ']'
            elif i == LOGIC_VAL_ERROR:
                stri = '-'
            elif i == LOGIC_VAL_UNKNOWN:
                stri = 'x'
            else:
                stri = str(i)

            result += '{}'.format(stri)

        return result

    def stripResultVect( vect ):
        result = []
        for i in range(0, len( vect )):
            if len( vect[i] ) > 1:
                result.append( vect[i] )
            else:
                result.append( (vect[i])[0] )

        return result


    print('\nWires')
    for (w, bus_num) in dSignal:
        if not( (w in linputname) or (w in loutputname) ) :
            print( '  {:20} : {}'.format(w+'['+str(bus_num)+']', vect_to_str( stripResultVect( dSignal[(w, bus_num)] ) )) )

    print('\nInputs')
    for (inp, _) in linputs:
        for vect_tuple in getSignalsWithName('', inp):
            vect_str = vect_to_str( stripResultVect(vect_tuple[1]) )
            print( '  {:10} : {}'.format(vect_tuple[0], vect_str) )

    print('\nOutputs')
    for out in loutputs:
        for vect_tuple in getSignalsWithName('', out):
            vect_str = vect_to_str( stripResultVect(vect_tuple[1]) )
            print( '  {:10} : {}'.format(vect_tuple[0], vect_str) )
    
    print('')
    return True
