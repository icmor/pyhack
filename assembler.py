import re

PREDEFINED_SYMBOLS = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}

JMP_TABLE = {"": 0b000,
             "JGT": 0b001,
             "JEQ": 0b010,
             "JGE": 0b011,
             "JLT": 0b100,
             "JNE": 0b101,
             "JLE": 0b110,
             "JMP": 0b111}

COMP_TABLE = {"0": 0b0101010 << 6,
              "1": 0b0111111 << 6,
              "-1": 0b0111010 << 6,
              "D": 0b0001100 << 6,
              "A": 0b0110000 << 6,
              "M": 0b1110000 << 6,
              "!D": 0b0001101 << 6,
              "!A": 0b0110001 << 6,
              "!M": 0b1110001 << 6,
              "-D": 0b0001111 << 6,
              "-A": 0b0110011 << 6,
              "-M": 0b1110011 << 6,
              "D+1": 0b0011111 << 6,
              "A+1": 0b0110111 << 6,
              "M+1": 0b1110111 << 6,
              "D-1": 0b0001110 << 6,
              "A-1": 0b0110010 << 6,
              "M-1": 0b1110010 << 6,
              "D+A": 0b0000010 << 6,
              "D+M": 0b1000010 << 6,
              "D-A": 0b0010011 << 6,
              "D-M": 0b1010011 << 6,
              "A-D": 0b0000111 << 6,
              "M-D": 0b1000111 << 6,
              "D&A": 0b0000000 << 6,
              "D&M": 0b1000000 << 6,
              "D|A": 0b0010101 << 6,
              "D|M": 0b1010101 << 6}


class HackSyntaxError(SyntaxError):
    pass


class HackValueError(ValueError):
    pass


def is_valid_symbol(symbol: str) -> bool:
    if symbol[0].isdigit():
        return False
    for c in symbol:
        if not c.isalnum() and c not in "_.$:":
            return False
    return True


def parse_label(instruction: str, lineno: int) -> str:
    label = instruction.removeprefix("(").removesuffix(")")
    if len(label) != len(instruction) - 2:
        raise HackSyntaxError(
            f"Malformed instruction {instruction} at line: {lineno}\n"
            "Labels must be in the format (ccc) where ccc is a valid symbol."
        )
    if is_valid_symbol(label):
        return label
    raise HackSyntaxError(
        f"Invalid label {label} at line: {lineno}\n"
        "Symbols cannot begin with a digit and can only contain letters, "
        "digits, dollar signs, dots, and underscores."
    )


def parse_ainst(instruction: str, lineno: int) -> str | int:
    symbol = instruction.removeprefix("@")
    if symbol.isdigit():
        address = int(symbol)
        if address >= 0x0 and address <= 0x7FFF:
            return address
        raise HackValueError(
            f"Invalid address {address} at line: {lineno}\n"
            "Numeric addresses must be in the range 0-32767."
        )
    if is_valid_symbol(symbol):
        return symbol
    raise HackSyntaxError(
        f"Invalid symbol {symbol} at line: {lineno}\n"
        "Symbols cannot begin with a digit and can only contain letters, "
        "digits, dollar signs, dots, and underscores."
    )


def parse_cinst(instruction: str, lineno: int) -> int:
    def parse_comp(comp: str) -> int:
        if COMP_TABLE.get(comp) is None:
            raise HackValueError(f"Unknown operation {comp} at line: {lineno}")
        return COMP_TABLE[comp]

    def parse_dest(dest: str) -> int:
        for i in range(len(dest)):
            if dest[i] not in "ADM":
                raise HackValueError(
                    f"Invalid assignment {dest} at line: {lineno}"
                )
            if dest[i] in dest[i+1:]:
                raise HackSyntaxError(
                    f"Duplicate assignments {dest} at line: {lineno}"
                )
        a = 0b100 if "A" in dest else 0
        d = 0b010 if "D" in dest else 0
        m = 0b001 if "M" in dest else 0
        return (a | d | m) << 3

    def parse_jump(jump: str) -> int:
        if JMP_TABLE.get(jump) is None:
            raise HackValueError(f"Invalid jump {jump} at line: {lineno}")
        return JMP_TABLE[jump]

    inst = 0b111 << 13
    match re.split(r"([=;])", instruction):
        case ['', '=', *_]:
            raise HackSyntaxError(
                f"Malformed C-instruction at line: {lineno}\n"
                "If dest part is empty omit the = symbol."
            )
        case [_, ';', ''] | [_, '=', _, ';', '']:
            raise HackSyntaxError(
                f"Malformed C-instruction at line: {lineno}\n"
                "If jump part is empty omit the ; symbol."
            )
        case [dest, '=', comp, ';', jump]:
            inst |= parse_dest(dest) | parse_comp(comp) | parse_jump(jump)
        case [dest, '=', comp]:
            inst |= parse_dest(dest) | parse_comp(comp)
        case [comp, ';', jump]:
            inst |= parse_comp(comp) | parse_jump(jump)
        case [comp]:
            inst |= parse_comp(comp)
        case _:
            raise HackSyntaxError(
                f"Unknown instruction \"{instruction}\" at line: {lineno}\n"
            )
    return inst


def assemble(code: list[str]) -> list[str]:
    symbols = PREDEFINED_SYMBOLS.copy()
    pending_labels = []
    assembly = []
    real_lineno = 0
    lineno = 0
    for line in code:
        line = line.strip()
        real_lineno += 1
        if line.startswith("//") or line == "":
            continue
        if line.startswith("("):    # label
            label = parse_label(line, real_lineno)
            if symbols.get(label) is not None:
                raise HackSyntaxError(
                    f"Repeated label {label} at line: {real_lineno}."
                )
            symbols[label] = lineno
            continue
        if line.startswith("@"):    # A instruction
            inst = parse_ainst(line, real_lineno)
            if type(inst) is str:
                if symbols.get(inst) is None:
                    # write label directly in the assembly for later resolution
                    assembly.append(inst)
                    pending_labels.append(lineno)
                    lineno += 1
                    continue
                inst = symbols[inst]
        else:                       # C instruction
            inst = parse_cinst(line, real_lineno)

        assembly.append(f"{inst:016b}\n")
        lineno += 1

    # resolve pending labels
    next_address = 16
    for lineno in pending_labels:
        label = assembly[lineno]
        if symbols.get(label) is None:
            symbols[label] = next_address
            next_address += 1
        inst = symbols[label]
        assembly[lineno] = f"{inst:016b}\n"

    return assembly
