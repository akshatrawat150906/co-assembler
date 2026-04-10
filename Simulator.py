register = [0] * 32
register[2] = 0x17C  
pc = 0
program_m = [0] * 64
data_m = {}  
halt = False

output_file = None


DATA_MIN = 0x00010000
DATA_MAX = 0x0001007F
STACK_MIN= 0x00000100 
STACK_MAX = 0x0000017F



def sign_extend(val, bits):
    val = val & ((1 << bits) - 1)
    signBit = 1 << (bits - 1)
    if val & signBit:
        val = val - (1 << bits)
    return val


def signed_32(val):
    val = val & 0xFFFFFFFF
    if val > 0x7FFFFFFF:
        val = val - 0x100000000
    return val

def unsigned_32(val):
    return val & 0xFFFFFFFF


def print_state():
    global output_file
    pc_val = pc & 0xFFFFFFFF
    parts = [f"0b{pc_val:032b}"]
    for i in range(32):
        val = register[i] & 0xFFFFFFFF
        parts.append(f"0b{val:032b}")
    output_file.write(" ".join(parts) + " \n")

def memory_print():
    global output_file
    for i in range(32):
        addr = 0x00010000 + i*4
        val = data_m.get(addr, 0) & 0xFFFFFFFF
        output_file.write(f"0x{addr:08X}:0b{val:032b}\n")

#--------------------------------------------------------------
def execute():
    global pc, halt

    
    if (pc // 4) >= 64:
        print(f"Error: PC {hex(pc)} is outside of the  instruction memory")
        import sys
        sys.exit(1)

    inst = program_m[pc // 4]
    opcode = inst & 0x7F
    rd = (inst >> 7) & 0x1F
    func3 = (inst >> 12) & 0x7
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    func7 = (inst >> 25) & 0x7F

    next_pc = pc + 4

        
    if opcode == 0x33:
        if func3 == 0x0:
            if func7 == 0x00: 
                register[rd] = register[rs1] + register[rs2]
            elif func7 == 0x20: 
                register[rd] = register[rs1] - register[rs2]
        
        elif func3 == 0x1: 
            register[rd] = register[rs1] << (register[rs2] & 0x1F)

            
        elif func3 == 0x2: 
            if signed_32(register[rs1]) < signed_32(register[rs2]):
                register[rd] = 1
            else:
                register[rd] = 0
                
        elif func3 == 0x3: 
            if unsigned_32(register[rs1]) < unsigned_32(register[rs2]):
                register[rd] = 1
            else:
                register[rd] = 0
                
        elif func3 == 0x4:
            register[rd] = register[rs1] ^ register[rs2]
            
        elif func3 == 0x5:
            if func7 == 0x00: 
                register[rd] = unsigned_32(register[rs1]) >> (register[rs2] & 0x1F)
                
        elif func3 == 0x6: 
            register[rd] = register[rs1] | register[rs2]
            
        elif func3 == 0x7: 
            register[rd] = register[rs1] & register[rs2]

    
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

    
    elif opcode == 0x67:
        imm = signed_32(sign_extend(inst >> 20, 12))
        target = (register[rs1] + imm) & 0xFFFFFFFF
        
        if target % 4 != 0:
            print(f"Alignment Error JALR target is not of the4-byte aligned")
            import sys
            sys.exit(1)
        register[rd] = (pc + 4) & 0xFFFFFFFF
        next_pc = target & 0xFFFFFFFE

    
    elif opcode == 0x6F:
        part_a = ((inst >> 31) << 20)
        part_b = (((inst >> 12) & 0xFF) << 12)
        part_c = (((inst >> 20) & 1) << 11)
        part_d = (((inst >> 21) & 0x3FF) << 1)

        all_bits = part_a |part_b | part_c |part_d

        evalue = sign_extend(all_bits, 21)
        imm = signed_32(evalue)

        register[rd] = (pc + 4) & 0xFFFFFFFF
        next_pc = (pc + imm) & 0xFFFFFFFF
        
        if next_pc % 4 != 0:
            print(f"Alignment Error  JAL target is not 4-byte aligned.")
            import sys
            sys.exit(1)

    
    elif opcode == 0x37:
        register[rd] = inst & 0xFFFFF000

    
    elif opcode == 0x17:
        register[rd] = (pc + (inst & 0xFFFFF000)) & 0xFFFFFFFF

    
    else:
        print(f"Errorin Execution Illegal opcode")
        import sys
        sys.exit(1)

    register[0] = 0
    pc = next_pc
    print_state()

    #------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
        for i, line in enumerate(lines):
            if i < 64:
                program_m[i] = int(line, 2)
        count = len(lines)

    output_file = open(output_file, 'w')

    while not halt and (pc // 4) < count:
        execute()

    memory_print()
    output_file.close()
