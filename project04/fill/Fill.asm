// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

// Put your code here.

// the program holds three variables:
// R0 - current screen address to color
// R1 - address of right after the end of the screen
// R2 - color to fill in {white = 0, black = -1}

(INIT)
    // init R0
    @SCREEN 
    D=A 
    @R0
    M=D 
    // init R1
    @24576
    D=A
    @R1
    M=D
    // init R2 to white as default
    @R2
    M=0 

(CHECK)  // check if user is pressing any key
    @KBD
    D=M
    @WHITE
    D;JEQ  // if D=0 fill in white
    @BLACK 
    0;JMP  // else fill in black

(FILL)
    @R2  // get the color to fill with
    D=M
    @R0  // access current screen pixel address
    A=M
    M=D  // fill
    
    @R0
    M=M+1  // increment current pixel address by 1
    D=M  // holds R0
    @R1
    D=D-M  // R0-R1 (R0-24576)
    @INIT
    D;JEQ  // if reached the end of the screen (address 8192) restart the program
    @FILL
    0;JMP // else continue filling

(BLACK)
    @R2
    M=-1
    @FILL
    0;JMP

(WHITE)
    @R2
    M=0
    @FILL
    0;JMP