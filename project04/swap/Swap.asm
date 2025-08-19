// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

@R14
D=M
@minid  // init min variable as first element's address
M=D
@maxid  // init max variable as first element's address
M=D
@i  // init index variable
M=1
@curid  // init current element address as 0
M=0

(TRAVERSE)
    @i
    D=M
    @R15  // array length 
    D=D-M
    @SWAP  // if reached end of array goto SWAP
    D;JEQ

    @R14
    D=M
    @i
    A=D+M  
    D=A
    @curid
    M=D  // current location in array

    // check min:
    @curid
    A=M
    D=M
    @minid
    A=M
    D=M-D
    @SWITCHMIN  // switch if current element is smaller
    D;JGT

    // check max:
    @curid
    A=M
    D=M
    @maxid
    A=M
    D=D-M
    @SWITCHMAX  // switch if current element is bigger
    D;JGT

    @i
    M=M+1
    @TRAVERSE
    0;JMP

(SWITCHMIN)
    @curid
    D=M /// QUESTION - DOES IT MATTER IF I WRITE HERE " D=A "?
    @minid
    M=D 
    @i
    M=M+1
    @TRAVERSE
    0;JMP

(SWITCHMAX)
    @curid
    D=M
    @maxid
    M=D
    @i
    M=M+1
    @TRAVERSE
    0;JMP

(SWAP)
    // switch min and max values:
    @maxid
    A=M 
    D=M
    @maxval
    M=D  

    @minid
    A=M  
    D=M 
    @minval
    M=D 

    @minval
    D=M
    @maxid
    A=M
    M=D

    @maxval
    D=M
    @minid
    A=M
    M=D
    
    @END
    0;JMP

(END)
    @END
    0;JMP
