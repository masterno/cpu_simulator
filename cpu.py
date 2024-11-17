from instruction_set import InstructionSet

class CPU:
    """CPU for MIPS simulator."""
    
    def __init__(self, memory_bus, instruction_set):
        """Initialize CPU."""
        self.memory_bus = memory_bus
        self.instruction_set = instruction_set
        self.reset()
        
    def reset(self):
        """Reset CPU state."""
        self.pc = 0  # Program counter
        self.registers = [0] * 32  # 32 general-purpose registers
        self.halted = False
        self.branch_taken = False
        self.branch_target = None
        
        # Initialize special registers
        self.registers[0] = 0  # $zero is always 0
        self.registers[29] = 0x7FFFFFFF  # $sp (stack pointer)
        self.registers[30] = 0  # $fp (frame pointer)
        self.registers[31] = 0  # $ra (return address)
        
    def run(self):
        """Run the CPU until halted."""
        while not self.halted:
            try:
                # Fetch instruction
                instruction = self.memory_bus.read_word(self.pc)
                
                # Decode instruction
                decoded = self.decode_instruction(instruction)
                
                # Execute instruction
                if decoded['opcode'] == 0x00:  # R-type
                    self._execute_r_type(decoded)
                elif decoded['opcode'] in [0x08, 0x23, 0x2B, 0x05, 0x04]:  # I-type
                    self._execute_i_type(decoded)
                elif decoded['opcode'] in [0x02, 0x03]:  # J-type
                    self._execute_j_type(decoded)
                elif decoded['opcode'] == 0x3F:  # HALT
                    print("\nCPU halted")
                    self.halted = True
                    break
                else:
                    raise ValueError(f"Unknown opcode: {hex(decoded['opcode'])}")
                
                # Update program counter
                self.update_pc()
                
            except Exception as e:
                print(f"\nError during execution at PC={hex(self.pc)}: {str(e)}")
                self.halted = True
                break
                
    def decode_instruction(self, instruction: int) -> dict:
        """Decode a 32-bit instruction."""
        opcode = (instruction >> 26) & 0x3F
        
        if opcode == 0x00:  # R-type
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            rd = (instruction >> 11) & 0x1F
            shamt = (instruction >> 6) & 0x1F
            funct = instruction & 0x3F
            return {
                'opcode': opcode,
                'rs': rs,
                'rt': rt,
                'rd': rd,
                'shamt': shamt,
                'funct': funct
            }
        elif opcode in [0x08, 0x23, 0x2B, 0x05, 0x04]:  # I-type
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            immediate = instruction & 0xFFFF
            # Sign extend immediate if needed
            if immediate & 0x8000:
                immediate |= -1 << 16
            return {
                'opcode': opcode,
                'rs': rs,
                'rt': rt,
                'immediate': immediate
            }
        elif opcode in [0x02, 0x03]:  # J-type
            target = instruction & 0x3FFFFFF
            return {
                'opcode': opcode,
                'target': target
            }
        elif opcode == 0x3F:  # HALT
            return {
                'opcode': opcode
            }
        else:
            raise ValueError(f"Unknown opcode: {hex(opcode)}")
            
    def execute_instruction(self, decoded_instr):
        """Execute a decoded instruction."""
        if decoded_instr['opcode'] == 0x00:  # R-type
            self._execute_r_type(decoded_instr)
        elif decoded_instr['opcode'] in [0x08, 0x23, 0x2B, 0x05, 0x04]:  # I-type
            self._execute_i_type(decoded_instr)
        elif decoded_instr['opcode'] in [0x02, 0x03]:  # J-type
            self._execute_j_type(decoded_instr)
        elif decoded_instr['opcode'] == 0x3F:  # HALT
            print("\nCPU halted")
            self.halted = True
            
    def _execute_r_type(self, decoded_instr):
        """Execute R-type instruction."""
        funct = decoded_instr['funct']
        rs = self.registers[decoded_instr['rs']]
        rt = self.registers[decoded_instr['rt']]
        rd_idx = decoded_instr['rd']
        
        if funct == 0x20:  # ADD
            self.registers[rd_idx] = self.instruction_set.add(rd_idx, rs, rt)
            print(f"ADD: r{rd_idx} = {hex(self.registers[rd_idx])} (r{decoded_instr['rs']} + r{decoded_instr['rt']})")
        elif funct == 0x22:  # SUB
            self.registers[rd_idx] = self.instruction_set.sub(rd_idx, rs, rt)
            print(f"SUB: r{rd_idx} = {hex(self.registers[rd_idx])} (r{decoded_instr['rs']} - r{decoded_instr['rt']})")
        elif funct == 0x2A:  # SLT
            self.registers[rd_idx] = self.instruction_set.slt(rd_idx, rs, rt)
            print(f"SLT: r{rd_idx} = {hex(self.registers[rd_idx])} (r{decoded_instr['rs']} < r{decoded_instr['rt']})")
            
        # Ensure R0 stays 0
        self.registers[0] = 0
    
    def _execute_i_type(self, decoded_instr):
        """Execute I-type instruction."""
        opcode = decoded_instr['opcode']
        rs = self.registers[decoded_instr['rs']]
        rt_idx = decoded_instr['rt']
        immediate = decoded_instr['immediate']
        
        # Sign extend immediate for arithmetic operations
        if opcode in [0x08, 0x23, 0x2B]:  # ADDI, LW, SW
            if immediate & 0x8000:
                immediate |= -1 << 16
        
        if opcode == 0x08:  # ADDI
            result = rs + immediate
            self.registers[rt_idx] = result & 0xFFFFFFFF
            print(f"ADDI: r{rt_idx} = {hex(self.registers[rt_idx])} (r{decoded_instr['rs']} + {hex(immediate)})")
        
        elif opcode == 0x23:  # LW
            addr = (rs + immediate) & 0xFFFFFFFF
            if addr >= self.memory_bus.MEMORY_SIZE:
                raise MemoryError(f"Load address out of bounds: {hex(addr)}")
            self.registers[rt_idx] = self.memory_bus.read_word(addr)
            print(f"LW: r{rt_idx} = {hex(self.registers[rt_idx])} (mem[{hex(addr)}])")
        
        elif opcode == 0x2B:  # SW
            addr = (rs + immediate) & 0xFFFFFFFF
            if addr >= self.memory_bus.MEMORY_SIZE:
                raise MemoryError(f"Store address out of bounds: {hex(addr)}")
            value = self.registers[rt_idx]
            self.memory_bus.write_word(addr, value)
            print(f"SW: mem[{hex(addr)}] = {hex(value)} (r{rt_idx})")
        
        elif opcode == 0x05:  # BNE
            if self.registers[decoded_instr['rs']] != self.registers[rt_idx]:
                # Sign extend immediate for branch offset
                if immediate & 0x8000:
                    immediate |= -1 << 16
                # Calculate branch target (PC-relative)
                self.branch_target = (self.pc + 4 + (immediate << 2)) & 0xFFFFFFFF
                self.branch_taken = True
                print(f"BNE: Taking branch from {hex(self.pc)} to {hex(self.branch_target)}")
            else:
                print(f"BNE: Branch not taken at {hex(self.pc)}")
        
        elif opcode == 0x04:  # BEQ
            if self.registers[decoded_instr['rs']] == self.registers[rt_idx]:
                # Sign extend immediate for branch offset
                if immediate & 0x8000:
                    immediate |= -1 << 16
                # Calculate branch target (PC-relative)
                self.branch_target = (self.pc + 4 + (immediate << 2)) & 0xFFFFFFFF
                self.branch_taken = True
                print(f"BEQ: Taking branch from {hex(self.pc)} to {hex(self.branch_target)}")
            else:
                print(f"BEQ: Branch not taken at {hex(self.pc)}")
        
        # Ensure R0 stays 0
        self.registers[0] = 0
    
    def _execute_j_type(self, decoded_instr):
        """Execute J-type instruction."""
        opcode = decoded_instr['opcode']
        target_addr = decoded_instr['target']
        
        if opcode == 0x02:  # J
            # Jump target is in the current 256MB region
            target = (self.pc & 0xF0000000) | (target_addr << 2)
            if target >= self.memory_bus.MEMORY_SIZE:
                raise MemoryError(f"Jump target out of bounds: {hex(target)}")
            print(f"J: Taking jump from {hex(self.pc)} to {hex(target)}")
            self.pc = target - 4  # -4 because we'll add 4 in update_pc()
        
        elif opcode == 0x03:  # JAL
            # Save return address (next instruction)
            return_addr = self.pc + 4
            self.registers[31] = return_addr  # Store return address in $ra
            
            # Jump target is in the current 256MB region
            target = (self.pc & 0xF0000000) | (target_addr << 2)
            if target >= self.memory_bus.MEMORY_SIZE:
                raise MemoryError(f"Jump target out of bounds: {hex(target)}")
            print(f"JAL: Taking jump-and-link from {hex(self.pc)} to {hex(target)}")
            self.pc = target - 4  # -4 because we'll add 4 in update_pc()
    
    def update_pc(self):
        """Update program counter."""
        if self.branch_taken:
            self.pc = self.branch_target
            self.branch_taken = False
            self.branch_target = None
        else:
            self.pc = (self.pc + 4) & 0xFFFFFFFF
        if self.pc >= self.memory_bus.MEMORY_SIZE:
            raise MemoryError(f"Program counter out of bounds: {hex(self.pc)}")
