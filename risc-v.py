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
S_TYPE = {
    "sw": "010",
}

mnemonic_opcode = {
    "add":   "0110011", 
    "sub":  "0110011",
    "sll":   "0110011", 
    "slt":  "0110011",
    "sltu":  "0110011", 
    "xor":  "0110011",
    "srl":   "0110011", 
    "or":   "0110011",
    "and":   "0110011",
    "lw":    "0000011",
    "addi":  "0010011", 
    "sltiu": "0010011",

    "jalr":  "1100111",
    "sw":    "0100011",

    "beq":   "1100011", 
    "bne":  "1100011",

    "blt":   "1100011", 
    "bge":  "1100011",

    "bltu":  "1100011", 
    "bgeu": "1100011",

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

opcode_select = {
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

def encode_s(imm_bin, rs2, rs1, funct3, opcode):
    upper = imm_bin[0:7]
    lower = imm_bin[7:12]
    return upper + rs2 + rs1 + funct3 + lower + opcode

def assemble_s(parts, line):
    op = parts[0]
    opcode = mnemonic_opcode[op]
    funct3 = S_TYPE[op]
    if len(parts) != 3:
        print(f"line {line}: {op} takes rs2, imm(rs1)")
        sys.exit(1)
    rs2 = get_register(parts[1], line)
    mem_operand = parts[2]
    imm = int(mem_operand[:mem_operand.index("(")])
    rs1_name = mem_operand[mem_operand.index("(")+1 : mem_operand.index(")")]
    rs1 = get_register(rs1_name, line)
    if imm < -2048 or imm > 2047:
        print(f"line {line}: immediate {imm} doesn't fit in 12 bits")
        sys.exit(1)
    imm_bin = to_binary(imm, 12)
    return encode_s(imm_bin, rs2, rs1, funct3, opcode)

def binary_convert(num ,bits):
    if num < 0:
        num = (1 << bits) +num
    b = bin(num)[2:]
    return b.zfill(bits)


def assemble_u(parts, line):
    op = parts[0]
    opcode = mnemonic_opcode[op]

    if len(parts) != 3:
        print(f"line {line}: {op} takes rd, imm")
        sys.exit(1)

    rd_name = parts[1].replace(",", "")
    rd = get_register(rd_name, line)

    imm = int(parts[2])
    if imm < 0 or imm > 1048575:
        print(f"line {line}: immediate {imm} doesn't fit in 20 bits")
        sys.exit(1)

    imm_bin = binary_convert(imm, 20)

    return imm_bin + rd + opcode
    
def encode_j(imm_bin, rd, opcode):
    imm20    = imm_bin[0]
    imm10_1  = imm_bin[10:20]
    imm11    = imm_bin[9]
    imm19_12 = imm_bin[1:9]
    return imm20 + imm10_1 + imm11 + imm19_12 + rd + opcode

def assemble_j(parts, line):
    op = parts[0]
    opcode = mnemonic_opcode[op]
    if len(parts) != 3:
        print(f"line {line}: jal takes rd, imm")
        sys.exit(1)
    rd_name = parts[1].replace(",", "")
    rd = get_register(rd_name, line)
    offset = int(parts[2])
    if offset % 2 != 0:
        print(f"line {line}: jump offset has to be even")
        sys.exit(1)
    if offset < -1048576 or offset > 1048574:
        print(f"line {line}: jump offset {offset} too big")
        sys.exit(1)
    imm_bin = binary_convert(offset, 21)
    return encode_j(imm_bin, rd, opcode)
