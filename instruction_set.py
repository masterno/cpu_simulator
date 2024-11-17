class InstructionSet:
    """
    MIPS instruction set implementation.
    Each method represents a MIPS instruction and performs the corresponding operation.
    All methods are static as they don't need instance state.
    """
    
    # R-type Instructions
    @staticmethod
    def add(rd, rs, rt):
        """Add: rd = rs + rt"""
        return rs + rt
    
    @staticmethod
    def sub(rd, rs, rt):
        """Subtract: rd = rs - rt"""
        return rs - rt
    
    @staticmethod
    def slt(rd, rs, rt):
        """Set Less Than: rd = 1 if rs < rt else 0"""
        return 1 if rs < rt else 0
        
    # I-type Instructions
    @staticmethod
    def addi(rt, rs, immediate):
        """Add Immediate: rt = rs + immediate"""
        return rs + immediate
    
    @staticmethod
    def lw(rt, rs, offset):
        """Load Word: rt = Memory[rs + offset]"""
        return rs + offset  # Returns address to load from
    
    @staticmethod
    def sw(rt, rs, offset):
        """Store Word: Memory[rs + offset] = rt"""
        return rs + offset  # Returns address to store to
    
    @staticmethod
    def bne(rs: int, rt: int, offset: int) -> bool:
        """Branch if not equal."""
        return rs != rt
        
    # J-type Instructions
    @staticmethod
    def j(target):
        """Jump: PC = (PC & 0xF0000000) | (target << 2)"""
        return target
    
    @staticmethod
    def jal(target, pc):
        """Jump and Link: r31 = PC + 4; PC = (PC & 0xF0000000) | (target << 2)"""
        return target, pc + 4
        
    # Special Instructions
    @staticmethod
    def halt():
        """Halt the CPU"""
        return True
