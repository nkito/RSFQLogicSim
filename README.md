# RSFQLogicSim - RSFQ Logic Simulation Tool

## What is this?
This logic simulation tool is designed for rapid single flux quantum (RSFQ) circuits. In RSFQ circuits, logic values are represented with voltage pulses. The order of voltage pulses affects the functionality of a gate.

The tool can handle the order of pulse arrivals explicitly.

## How to use?

The logic simulation tool works with Python3. Following packages are necessary to use the tool.

- [PLY (Python Lex-Yacc)](http://www.dabeaz.com/ply/index.html)

## Description for the tool

For logic simulation with the tool, a circuit description is necessary. The following is an example of the circuit description.

```
# 
# 4 bit multiplier
# 
 
# definition of a constant.
const WIDTH = 4;
 
## input and input pattern definitions.
#input reset_in [0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0];
#input load_in  [0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0];
#input y_in     [0,0,0,0,0,0,0,1,1,1,1,0,0,1,0,1,0,0,0,0,0,0,0];
#input x_in     [0,0,0,0,0,0,0,1,0,1,1,0,0,1,1,1,0,0,0,0,0,0,0];
#input s_in     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
input clk      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1];
 
# output definitions.
output reset_out;
output load_out;
output y_out;
output x_out;
output s_out;
 
module PE(s_out, L_out, X_out, R_out)(y_in, s_in, L_in, X_in, R_in, clk);
    wire Y, PP, S0, C0, C1T, C1;
 
    Y     = ND G1_1( L_in@0, y_in@1, L_in@2 );
    PP    = ND G2_1( L_in@0,    Y@1, X_in@2 );
     
    S0    = XOR G3_1( PP@0, s_in@0, clk@1 );
    C0    = AND G4_1( PP@0, s_in@0, clk@1 );
     
     
    s_out = XOR G5_1( S0@0, C1@0, clk@1 );
    C1T   = AND G6_1( S0@0, C1@0, clk@1 );
     
    C1    = CB G7_1( C1T@0, C0@0 );
     
    L_out = D G8_1 (L_in@1, clk@0 );
    X_out = D G10_1(X_in@1, clk@0 );
    R_out = D G11_1(R_in@1, clk@0 );
endmodule
 
# circuit definition
{
    # wire definitions
    wire L[0:`WIDTH-1], X[0:`WIDTH-1], R[0:`WIDTH-1];
    wire ser_out[1:`WIDTH-1], ser_in[0:`WIDTH-1];
    genvar i;
 
    assign ser_in[0] = s_in;
    assign L[0]      = load_in;
    assign X[0]      = x_in;
    assign R[0]      = reset_in;
 
    for u0 (i=0; i < `WIDTH-1; i += 1 ){
        (ser_out[i+1], L[i+1], X[i+1], R[i+1]) = PE PE0(y_in,  ser_in[i], L[i], X[i], R[i], clk);
        ser_in[i+1] = NDRO ND0( R[i+1]@2, L[i+1]@2, ser_out[i+1]@3);
    }
 
    (s_out, load_out, x_out, reset_out) = PE PE3(y_in, ser_in[`WIDTH-1], L[`WIDTH-1], X[`WIDTH-1], R[`WIDTH-1], clk);
 
    assign y_out     = y_in;
}
```
To run the tool, sfqsim.sh script is used. The source description is specified as the argument.

```
$ python3 src/sfqsim.py  circuits/mult4.sfqv 
```

The tool outputs following results with the above description.
```
Execute 23 cycles
 
Wires
  ser_in[0]            : 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  PE3.R_in[0]          : x, x, x, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0
  PE3.Y[0]             : x, x, x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0
  PE0_u0_loop=0.L_out[0] : x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
  PE0_u0_loop=0.PP[0]  : 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  PE0_u0_loop=2.y_in[0] : 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0
...
  PE0_u0_loop=1.L_out[0] : x, x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0
  PE0_u0_loop=0.clk[0] : 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
  PE0_u0_loop=1.clk[0] : 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
  PE0_u0_loop=2.PP[0]  : x, x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
 
Inputs
  reset_in   : 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  load_in    : 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  y_in       : 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0
  x_in       : 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0
  s_in       : 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  clk        : 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
 
Outputs
  reset_out  : x, x, x, x, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0
  load_out   : x, x, x, x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0
  y_out      : 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0
  x_out      : x, x, x, x, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0
  s_out      : x, x, x, x, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0
```



  
  
  
  
