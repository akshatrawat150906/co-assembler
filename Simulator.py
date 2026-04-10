elif opcode == 0x67:
    imm = signed_32(sign_extend(inst >> 20, 12))
    target = (register[rs1] + imm) & 0xFFFFFFFF
    
    if target % 4 != 0:
        print(f"Alignment Error JALR target is not of the4-byte aligned")
        import sys
        sys.exit(1)
    register[rd] = (pc + 4) & 0xFFFFFFFF
    next_pc = target & 0xFFFFFFFE
