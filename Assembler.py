import sys

registers = {
    "zero": "00000", "x0":  "00000",
    "ra":   "00001", "x1":  "00001",
    "sp":   "00010", "x2":  "00010",
    "gp":   "00011", "x3":  "00011",
    "tp":   "00100", "x4":  "00100",
    "t0":   "00101", "x5":  "00101",
    "t1":   "00110", "x6":  "00110",
    "t2":   "00111", "x7":  "00111",
    "s0":   "01000", "fp":  "01000", "x8":  "01000",
    "s1":   "01001", "x9":  "01001",
    "a0":   "01010", "x10": "01010",
    "a1":   "01011", "x11": "01011",
    "a2":   "01100", "x12": "01100",
    "a3":   "01101", "x13": "01101",
    "a4":   "01110", "x14": "01110",
    "a5":   "01111", "x15": "01111",
    "a6":   "10000", "x16": "10000",
    "a7":   "10001", "x17": "10001",
    "s2":   "10010", "x18": "10010",
    "s3":   "10011", "x19": "10011",
    "s4":   "10100", "x20": "10100",
    "s5":   "10101", "x21": "10101",
    "s6":   "10110", "x22": "10110",
    "s7":   "10111", "x23": "10111",
    "s8":   "11000", "x24": "11000",
    "s9":   "11001", "x25": "11001",
    "s10":  "11010", "x26": "11010",
    "s11":  "11011", "x27": "11011",
    "t3":   "11100", "x28": "11100",
    "t4":   "11101", "x29": "11101",
    "t5":   "11110", "x30": "11110",
    "t6":   "11111", "x31": "11111",
}

mnemonicOpcode = {
    "add":   "0110011", "sub":  "0110011",
    "sll":   "0110011", "slt":  "0110011",
    "sltu":  "0110011", "xor":  "0110011",
    "srl":   "0110011", "or":   "0110011",
    "and":   "0110011",
    "lw":    "0000011",
    "addi":  "0010011", "sltiu": "0010011",
    "jalr":  "1100111",
    "sw":    "0100011",
    "beq":   "1100011", "bne":  "1100011",
    "blt":   "1100011", "bge":  "1100011",
    "bltu":  "1100011", "bgeu": "1100011",
    "lui":   "0110111",
    "auipc": "0010111",
    "jal":   "1101111",
}

R_TYPE = {
    "add":  ("0000000", "000"),
    "sub":  ("0100000", "000"),
    "sll":  ("0000000", "001"),
    "slt":  ("0000000", "010"),
    "sltu": ("0000000", "011"),
    "xor":  ("0000000", "100"),
    "srl":  ("0000000", "101"),
    "or":   ("0000000", "110"),
    "and":  ("0000000", "111"),
}

I_TYPE = {
    "lw":    "010",
    "addi":  "000",
    "sltiu": "011",
    "jalr":  "000",
}

S_TYPE = {
    "sw": "010",
}

B_TYPE = {
    "beq":  "000",
    "bne":  "001",
    "blt":  "100",
    "bge":  "101",
    "bltu": "110",
    "bgeu": "111",
}

Halt = "00000000000000000000000001100011"


def error(msg):
    print(msg)
    sys.exit(1)


def get_register(reg, line):
    reg = reg.strip()
    if reg not in registers:
        error(f"error on line {line}: Invalid register name {reg}")
    return registers[reg]


def to_binary(value, bits):
    if value < 0:
        value = (1 << bits) + value
    return format(value, f"0{bits}b")


def single_line(line):
    line = line.strip()
    if not line:
        return None
    
    if line.endswith(":") and len(line.split()) == 1:
        return "__label__", [line[:-1]]
    
    if ":" in line:
        colon = line.index(":")
        label = line[:colon].strip()
        rest  = line[colon+1:].strip()
        if rest:
            result   = rest.split(None, 1)
            mnemonic = result[0].lower()
            operands = [op.strip() for op in result[1].replace(",", " ").split()] if len(result) > 1 else []
            return mnemonic, operands, label
    result   = line.split(None, 1)
    mnemonic = result[0].lower()
    if len(result) < 2:
        return mnemonic, []
    operands = [op.strip() for op in result[1].replace(",", " ").split()]
    return mnemonic, operands


def encode_r(funct7, rs2, rs1, funct3, rd, opcode):
    return funct7 + rs2 + rs1 + funct3 + rd + opcode

def assemble_r(list, line):
    op = list[0]
    opcode = mnemonicOpcode[op]
    funct7, funct3 = R_TYPE[op]
    if len(list) != 4:
        error(f"error on the line {line} and the {op} needs rd, rs1, rs2")
    rd  = get_register(list[1], line)
    rs1 = get_register(list[2], line)
    rs2 = get_register(list[3], line)
    return encode_r(funct7, rs2, rs1, funct3, rd, opcode)


def encode_i(imm_binary, rs1, funct3, rd, opcode):
    return imm_binary + rs1 + funct3 + rd + opcode

def assemble_i(list, line):
    op = list[0]
    opcode = mnemonicOpcode[op]
    funct3 = I_TYPE[op]
    if op in ("addi", "sltiu"):
        if len(list) != 4:
            error(f"error on the line {line} and  {op} needs rd, rs1, imm")
        rd  = get_register(list[1], line)
        rs1 = get_register(list[2], line)
        imm = int(list[3], 10)
    elif op == "jalr":
        
        if len(list) == 4:
            rd  = get_register(list[1], line)
            rs1 = get_register(list[2], line)
            imm = int(list[3], 10)
        elif len(list) == 3 and "(" in list[2]:
            rd = get_register(list[1], line)
            mem_operand = list[2]
            imm = int(mem_operand[:mem_operand.index("(")], 10)
            rs1_name = mem_operand[mem_operand.index("(")+1 : mem_operand.index(")")]
            rs1 = get_register(rs1_name, line)
        else:
            error(f"error on line {line}: jalr needs rd, rs1, imm or rd, imm(rs1)")
    else:
        if len(list) != 3:
            error(f"error on line {line}: {op} needs rd, imm(rs1)")
        rd          = get_register(list[1], line)
        mem_operand = list[2]
        imm         = int(mem_operand[:mem_operand.index("(")], 10)
        rs1_name    = mem_operand[mem_operand.index("(")+1 : mem_operand.index(")")]
        rs1         = get_register(rs1_name, line)
    if imm < -2048 or imm > 2047:
        error(f"error on line {line}and immediate {imm} out of range for 12 bits")
    imm_binary = to_binary(imm, 12)
    return encode_i(imm_binary, rs1, funct3, rd, opcode)


def encode_s(imm_binary, rs2, rs1, funct3, opcode):
    imm11_5 = imm_binary[0:7]
    imm4_0  = imm_binary[7:12]
    return imm11_5 + rs2 + rs1 + funct3 + imm4_0 + opcode

def assemble_s(list, line):
    op     = list[0]
    opcode = mnemonicOpcode[op]
    funct3 = S_TYPE[op]
    if len(list) != 3:
        error(f"error on line {line}: {op} it would need the rs2, imm(rs1)")
    rs2 = get_register(list[1], line)
    mem_operand = list[2]
    imm = int(mem_operand[:mem_operand.index("(")], 10)
    rs1_name = mem_operand[mem_operand.index("(")+1 : mem_operand.index(")")]
    rs1 = get_register(rs1_name, line)
    if imm < -2048 or imm > 2047:
        error(f"error on line {line}: immediate {imm} out of range for 12 bits")
    imm_binary = to_binary(imm, 12)
    return encode_s(imm_binary, rs2, rs1, funct3, opcode)


def encode_b(rs1, rs2, funct3, opcode, offset, line):
    if offset % 2 != 0:
        error(f"error on line {line} and branch offset must be even")
    if offset < -4096 or offset > 4094:
        error(f"error on line {line}and   branch offset {offset} out of range")
    rs1_bin = get_register(rs1, line)
    rs2_bin = get_register(rs2, line)
    imm = to_binary(offset, 13)
    imm12 = imm[0]
    imm10_5 = imm[2:8]
    imm4_1 = imm[8:12]
    imm11 = imm[1]
    return imm12 + imm10_5 + rs2_bin + rs1_bin + funct3 + imm4_1 + imm11 + opcode

def assemble_b(list, line, labels, pc):
    op     = list[0]
    opcode = mnemonicOpcode[op]
    funct3 = B_TYPE[op]
    if len(list) != 4:
        error(f"error on line {line}and  {op} needs rs1, rs2, label/imm")
    rs1 = list[1]
    rs2 = list[2]
    target = list[3]
    offset = labels[target] - pc if target in labels else int(target, 10)
    return encode_b(rs1, rs2, funct3, opcode, offset, line)


def encode_u(imm_binary, rd, opcode):
    return imm_binary + rd + opcode

def assemble_u(list, line):
    op     = list[0]
    opcode = mnemonicOpcode[op]
    if len(list) != 3:
        error(f"error on line {line} and {op} needs rd, imm")
    rd  = get_register(list[1], line)
    imm = int(list[2], 10)
    if imm < -524288 or imm > 524287:
        error(f"error on line {line} and immediate {imm} out of range for 20 bits")
    imm_binary = to_binary(imm, 20)
    return encode_u(imm_binary, rd, opcode)


def encode_j(imm_binary, rd, opcode):
    imm20 = imm_binary[0]
    imm10_1 = imm_binary[10:20]
    imm11 = imm_binary[9]
    imm19_12 = imm_binary[1:9]
    return imm20 + imm10_1 + imm11 + imm19_12 + rd + opcode

def assemble_j(list, line, labels, pc):
    op = list[0]
    opcode = mnemonicOpcode[op]
    if len(list) != 3:
        error(f"error on line {line} jal needs rd, label/imm")
    rd = get_register(list[1], line)
    target = list[2]
    offset = labels[target] - pc if target in labels else int(target, 10)
    if offset % 2 != 0:
        error(f"error on line {line} offset must be even")
    if offset < -1048576 or offset > 1048574:
        error(f"error on line {line}  offset {offset} out of range")
    imm_binary = to_binary(offset, 21)
    return encode_j(imm_binary, rd, opcode)


opcode_Select = {
    "0110011": assemble_r,
    "0000011": assemble_i,
    "0010011": assemble_i,
    "1100111": assemble_i,
    "0100011": assemble_s,
    "1100011": assemble_b,
    "0110111": assemble_u,
    "0010111": assemble_u,
    "1101111": assemble_j,
}


def assemble(program):
    lines  = program.splitlines()
    labels = {}
    pc     = 0

    for i in lines:
        stripped = i.strip()
        if not stripped:
            continue
        if ":" in stripped:
            colon = stripped.index(":")
            label = stripped[:colon].strip()
            if not label[0].isalpha():
                error(f"error and label '{label}' must start with a letter")
            labels[label] = pc
            rest = stripped[colon+1:].strip()
            if rest:
                pc += 4
        else:
            pc += 4

    if pc > 256:
        error(f"error and program is too large {pc} bytes , max is 256 bytes")
#-----------------------------
    results    = []
    pc         = 0
    line_num   = 0
    halt_index = None

    for i in lines:
        line_num += 1
        parsed = single_line(i)
        if parsed is None:
            continue
        if parsed[0] == "__label__":
            continue

        if len(parsed) == 3:
            mnemonic, operands, _ = parsed
        else:
            mnemonic, operands = parsed

        if mnemonic not in mnemonicOpcode:
            error(f"error on line {line_num} and unknown instruction '{mnemonic}'")

        opcode      = mnemonicOpcode[mnemonic]
        assemble_fn = opcode_Select[opcode]
        list       = [mnemonic] + operands

        if opcode in ("1100011", "1101111"):
            binary = assemble_fn(list, line_num, labels, pc)
        else:
            binary = assemble_fn(list, line_num)

        if binary == Halt:
            halt_index = len(results)

        results.append(binary)
        pc += 4

    if not results:
        error("error: empty program")
    if halt_index is None:
        error("error: missing virtual halt (beq zero, zero, 0)")

    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python assembler.py <input.asm> <output.bin>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r") as f:
            program = f.read()
    except FileNotFoundError:
        error(f"error and input file {sys.argv[1]} not found")

    results = assemble(program)

    with open(sys.argv[2], "w") as f:
        for binary in results:
            f.write(binary + "\n")
