SEGMENTS = {"local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"}

# push <segment> <index> (mem[sp++] = segment[index])
# pushes need to load data unto D register
PUSH_POSTAMBLE_ASM = """\
@SP
A=M
M=D
@SP
M=M+1
"""

PUSH_CONSTANT_ASM = """\
@%s
D=A
""" + PUSH_POSTAMBLE_ASM

PUSH_DIRECT_ASM = """\
@%s
D=M
""" + PUSH_POSTAMBLE_ASM

PUSH_SEGMENT_ASM = """\
@%(index)s
D=A
@%(segment)s
A=D+M
D=M
""" + PUSH_POSTAMBLE_ASM

POP_DIRECT_ASM = """\
@SP
AM=M-1
D=M
@%s
M=D
"""

POP_SEGMENT_ASM = """\
@%(index)s
D=A
@%(segment)s
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
"""


def memory_instruction(instruction: str, segment: str, index: str, prog: str) -> str:
    if instruction == "push":
        if segment == "constant":
            return PUSH_CONSTANT_ASM % index
        if segment == "pointer":
            return PUSH_DIRECT_ASM % ("THIS" if index == "0" else "THAT")
        if segment == "temp":
            return PUSH_DIRECT_ASM % str(int(index) + 5)
        if segment == "static":
            return PUSH_DIRECT_ASM % (prog + '.' + str(index))
        return PUSH_SEGMENT_ASM % {"segment": SEGMENTS[segment], "index": index}
    else:
        if segment == "pointer":
            return POP_DIRECT_ASM % ("THIS" if index == "0" else "THAT")
        if segment == "temp":
            return POP_DIRECT_ASM % str(int(index) + 5)
        if segment == "static":
            return POP_DIRECT_ASM % (prog + '.' + str(index))
        return POP_SEGMENT_ASM % {"segment": SEGMENTS[segment], "index": index}
