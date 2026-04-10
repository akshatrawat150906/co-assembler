elif opcode == 0x13:
    imm = signed_32(sign_extend(inst >> 20, 12))
    
    if func3 == 0x0: 
        register[rd] = register[rs1] + imm
        
    elif func3 == 0x2: 
        if signed_32(register[rs1]) < imm:
            register[rd] = 1
        else:
            register[rd] = 0
            
    elif func3 == 0x3: 
        if unsigned_32(register[rs1]) < unsigned_32(imm):
            register[rd] = 1
        else:
            register[rd] = 0

elif opcode == 0x03:
    imm = signed_32(sign_extend(inst >> 20, 12))
    addr = (register[rs1] + imm) & 0xFFFFFFFF
    

    if not (DATA_MIN <= addr <= DATA_MAX or STACK_MIN <= addr <= STACK_MAX):
        print(f"Memory Access Error Load address are out of bounds")
        import sys
        sys.exit(1)
    register[rd] = data_m.get(addr, 0)


elif opcode == 0x67:
    imm = signed_32(sign_extend(inst >> 20, 12))
    target = (register[rs1] + imm) & 0xFFFFFFFF
    
    if target % 4 != 0:
        print(f"Alignment Error JALR target is not of the4-byte aligned")
        import sys
        sys.exit(1)
    register[rd] = (pc + 4) & 0xFFFFFFFF
    next_pc = target & 0xFFFFFFFE

elif opcode == 0x37:
    register[rd] = inst & 0xFFFFF000

elif opcode == 0x17:
    register[rd] = (pc + (inst & 0xFFFFF000)) & 0xFFFFFFFF


    inst = program_m[pc // 4]
    opcode = inst & 0x7F
    rd = (inst >> 7) & 0x1F
    func3 = (inst >> 12) & 0x7
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    func7 = (inst >> 25) & 0x7F
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    func7 = (inst >> 25) & 0x7F

    next_pc = pc + 4
elif opcode == 0x23:
        imm = signed_32(sign_extend(((inst >> 25) << 5) | ((inst >> 7) & 0x1F), 12))
        addr = (register[rs1] + imm) & 0xFFFFFFFF
        
        if not (DATA_MIN <= addr <= DATA_MAX or STACK_MIN <= addr <= STACK_MAX):
            print(f"Memory Access Errors Store address out of bounds")
            import sys
            sys.exit(1)
        data_m[addr] = register[rs2]

elif opcode == 0x63:
    part_a = ((inst >> 31) << 12)
    part_b = (((inst >> 7) & 1) << 11)
    part_c = (((inst >> 25) & 0x3F) << 5)
    part_d = (((inst >> 8) & 0xF) << 1)

    all_bits = part_a| part_b | part_c| part_d
    
    evalue = sign_extend(all_bits, 13)
    imm = signed_32(evalue)

    take_branch = False
    if func3 == 0x0: take_branch = (register[rs1] == register[rs2])
    elif func3 == 0x1: take_branch = (register[rs1] != register[rs2])
    elif func3 == 0x4: take_branch = (signed_32(register[rs1]) < signed_32(register[rs2]))
    elif func3 == 0x5: take_branch = (signed_32(register[rs1]) >= signed_32(register[rs2]))
    elif func3 == 0x6: take_branch = (unsigned_32(register[rs1]) < unsigned_32(register[rs2]))
    elif func3 == 0x7: take_branch = (unsigned_32(register[rs1]) >= unsigned_32(register[rs2]))

    if take_branch:
        next_pc = (pc + imm) & 0xFFFFFFFF
        if next_pc == pc:
            halt = True

