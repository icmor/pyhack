# D register contains second operand and M contains first operand.
# We don't care about the order of the operands except for substraction since
# it's not commutative.
BINOP_ASM = """\
@SP
AM=M-1
D=M
@SP
A=M-1
%s
"""

UOP_ASM = """\
@SP
A=M-1
%s
"""

LOGIC_ASM = """\
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
M=-1
@CMP%(uid)d
D;%(cmp)s
@SP
A=M-1
M=0
(CMP%(uid)d)
"""

def arith_instruction(op: str) -> str:
    if op == "add":
        return BINOP_ASM % "M=D+M"
    if op == "sub":
        return BINOP_ASM % "M=M-D"
    if op == "neg":
        return UOP_ASM % "M=-M"
    if op == "eq":
        arith_instruction.uid += 1
        return LOGIC_ASM % {"uid": arith_instruction.uid, "cmp": "JEQ"}
    if op == "gt":
        arith_instruction.uid += 1
        return LOGIC_ASM % {"uid": arith_instruction.uid, "cmp": "JGT"}
    if op == "lt":
        arith_instruction.uid += 1
        return LOGIC_ASM % {"uid": arith_instruction.uid, "cmp": "JLT"}
    if op == "or":
        return BINOP_ASM % "M=D|M"
    if op == "and":
        return BINOP_ASM % "M=D&M"
    if op == "not":
        return UOP_ASM % "M=!M"
arith_instruction.uid = 0
