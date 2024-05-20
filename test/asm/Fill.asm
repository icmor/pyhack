// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed,
// the screen should be cleared.

// R0 = SCREEN[0]
@SCREEN
D=A
@R0
M=D

// R1 = length(SCREEN)
@8192
D=D+A
@R1
M=D

(LOOP)
@KBD
D=M
// KBD > 0 GOTO PRESS
@PRESS
D;JGT
// KBD == 0 GOTO NOPRESS
@NOPRESS
D;JEQ

(NOPRESS)
// paint 16 pixels white
@R0
A=M
M=0

// R0 == SCREEN[0] GOTO LOOP
@SCREEN
D=A
@R0
D=M-D
@LOOP
D;JEQ

// R0 = R0 - 1
@R0
M=M-1

@LOOP
0;JMP

(PRESS)
// paint 16 pixels black
@R0
A=M
M=-1

// R0 + 1 == R1 GOTO LOOP
@R0
D=M+1
@R1
D=M-D
@LOOP
D;JEQ

// R0 = R0 + 1
@R0
M=M+1

@LOOP
0;JMP
