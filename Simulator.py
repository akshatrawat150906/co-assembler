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



