S_TYPE = {
    "sw": "010",
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