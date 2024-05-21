from pathlib import Path
import arith
import memory

ASM_POSTAMBLE = """\
@LOOP
(LOOP)
0;JMP
"""

if __name__ == "__main__":
    for file in Path("test").glob("*vm"):
        asm = []
        with file.open() as f:
            code = f.readlines()
        for line in code:
            line = line.strip()
            if line.startswith("//") or not line:
                continue
            asm.append("//" + line + "\n")
            match line.split():
                case [("push" | "pop") as instruction, segment, index]:
                    asm.append(memory.memory_instruction(instruction, segment, index, file.name))
                case [op] if op in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
                    asm.append(arith.arith_instruction(op))
        asm.append(ASM_POSTAMBLE)

        with file.with_suffix(".asm").open('w') as f:
            f.writelines(asm)
