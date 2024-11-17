import re
from typing import Dict, List, Tuple, Union
import struct

class InstructionParserError(Exception):
    """Custom exception for instruction parsing errors."""
    pass

class InstructionParser:
    # Instruction formats and opcodes
    R_TYPE_OPCODES = {
        'ADD': 0x00,
        'SUB': 0x00,
        'SLT': 0x00
    }
    
    R_TYPE_FUNCTS = {
        'ADD': 0x20,
        'SUB': 0x22,
        'SLT': 0x2A
    }
    
    I_TYPE_OPCODES = {
        'ADDI': 0x08,
        'LW': 0x23,
        'SW': 0x2B,
        'BNE': 0x05,
        'BEQ': 0x04,
    }
    
    J_TYPE_OPCODES = {
        'J': 0x02,
        'JAL': 0x03,
    }
    
    SPECIAL_INSTRUCTIONS = {
        'HALT': 0x3F,  # Special opcode for HALT
        'CACHE': 0x3E,  # Custom opcode for CACHE
    }
    
    def __init__(self):
        """Initialize instruction parser."""
        # Initialize state
        self.current_address = 0
        self.symbol_table = {}
        self.machine_code = bytearray()
    
    def parse_file(self, filename: str) -> None:
        """Parse assembly file and generate machine code."""
        # First pass: collect labels
        self.current_address = 0
        self.symbol_table = {}
        
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Remove inline comments
                if '#' in line:
                    line = line[:line.index('#')].strip()
                    
                # Check for label
                if ':' in line:
                    label, rest = line.split(':', 1)
                    label = label.strip()
                    self.symbol_table[label] = self.current_address
                    line = rest.strip()
                    if not line:  # If line only contained label
                        continue
                        
                self.current_address += 4  # Each instruction is 4 bytes
        
        # Second pass: generate machine code
        self.current_address = 0
        self.machine_code = bytearray()
        
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Remove inline comments
                if '#' in line:
                    line = line[:line.index('#')].strip()
                    
                # Remove label if present
                if ':' in line:
                    _, line = line.split(':', 1)
                    line = line.strip()
                    if not line:
                        continue
                        
                # Parse instruction
                parts = line.replace(',', ' ').split()
                instruction = self._parse_instruction(parts)
                self.machine_code.extend(instruction.to_bytes(4, byteorder='big'))
                self.current_address += 4
    
    def parse_memory_init(self, file_path: str) -> Dict[int, int]:
        """
        Parse memory initialization data from a file.
        
        Args:
            file_path: Path to the memory initialization file
            
        Returns:
            Dictionary mapping addresses to initial values
        """
        memory_data = {}
        
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse address:data format
                    try:
                        addr_str, data_str = line.split(':')
                        # Remove any comments from data
                        data_str = data_str.split('#')[0].strip()
                        
                        address = self._parse_number(addr_str.strip())
                        data = self._parse_number(data_str.strip())
                        
                        if address % 4 != 0:
                            raise InstructionParserError(f"Address must be word-aligned: {hex(address)}")
                            
                        memory_data[address] = data
                        
                    except ValueError:
                        raise InstructionParserError(f"Invalid memory initialization format on line {line_num}")
                        
        except FileNotFoundError:
            raise InstructionParserError(f"Memory initialization file not found: {file_path}")
            
        return memory_data
    
    def _first_pass(self, file_path: str) -> None:
        """Collect all labels and their addresses."""
        current_address = 0
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Remove comments from the line
                line = line.split('#')[0].strip()
                
                # Check for labels
                if ':' in line:
                    label = line.split(':')[0].strip()
                    self.symbol_table[label] = current_address
                    
                # Only increment address for actual instructions
                if not line.endswith(':'):
                    current_address += 4
    
    def _parse_instruction(self, parts: List[str]) -> int:
        """Parse a single instruction into machine code."""
        # Get instruction type
        instruction = parts[0].upper()
        
        if instruction in self.R_TYPE_OPCODES:
            return self._parse_r_type(parts)
        elif instruction in self.I_TYPE_OPCODES:
            return self._parse_i_type(parts)
        elif instruction in self.J_TYPE_OPCODES:
            return self._parse_j_type(parts)
        elif instruction in self.SPECIAL_INSTRUCTIONS:
            return self._parse_special_instruction(parts)
        else:
            raise InstructionParserError(f"Unknown instruction: {instruction}")
    
    def _parse_r_type(self, parts: List[str]) -> int:
        """Parse R-type instruction."""
        if len(parts) != 4:
            raise InstructionParserError(f"Invalid R-type instruction format: {' '.join(parts)}")
            
        opcode = self.R_TYPE_OPCODES[parts[0].upper()]
        funct = self.R_TYPE_FUNCTS[parts[0].upper()]
        rd = self._parse_register(parts[1])
        rs = self._parse_register(parts[2])
        rt = self._parse_register(parts[3])
        
        return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | funct
    
    def _parse_i_type(self, parts: List[str]) -> int:
        """Parse I-type instruction."""
        opcode = self.I_TYPE_OPCODES[parts[0].upper()]
        
        if parts[0].upper() in ['LW', 'SW']:
            # Handle memory access format: LW rt, offset(rs)
            if len(parts) != 3:
                raise InstructionParserError(f"Invalid memory access format: {' '.join(parts)}")
                
            rt = self._parse_register(parts[1])
            # Parse offset(rs) format
            offset_base = parts[2].strip()
            # Handle hex numbers in offset
            match = re.match(r'(-?(?:0x)?[0-9a-fA-F]+)\((\$\w+)\)', offset_base)
            if not match:
                raise InstructionParserError(f"Invalid memory access format: {offset_base}")
            
            try:
                immediate = self._parse_number(match.group(1))
                # Sign extend 16-bit immediate
                immediate = immediate & 0xFFFF
                if immediate & 0x8000:
                    immediate |= -1 << 16
            except InstructionParserError:
                raise InstructionParserError(f"Invalid offset in memory access: {match.group(1)}")
                
            rs = self._parse_register(match.group(2))
            
        elif parts[0].upper() == 'BNE':
            # Handle branch instruction: BNE rs, rt, label
            if len(parts) != 4:
                raise InstructionParserError(f"Invalid branch instruction format: {' '.join(parts)}")
                
            rs = self._parse_register(parts[1])
            rt = self._parse_register(parts[2])
            
            # Calculate branch offset
            label = parts[3].strip()
            if label not in self.symbol_table:
                raise InstructionParserError(f"Undefined label: {label}")
                
            # Calculate relative branch offset in words (4 bytes per word)
            target_addr = self.symbol_table[label]
            current_addr = self.current_address + 4  # PC points to next instruction
            offset = (target_addr - current_addr) >> 2  # Divide by 4 to get word offset
            
            # Check if offset fits in 16 bits
            if not -32768 <= offset <= 32767:
                raise InstructionParserError(f"Branch offset too large: {offset}")
                
            immediate = offset & 0xFFFF
            
        elif parts[0].upper() == 'BEQ':
            # Handle branch instruction: BEQ rs, rt, label
            if len(parts) != 4:
                raise InstructionParserError(f"Invalid branch instruction format: {' '.join(parts)}")
                
            rs = self._parse_register(parts[1])
            rt = self._parse_register(parts[2])
            
            # Calculate branch offset
            label = parts[3].strip()
            if label not in self.symbol_table:
                raise InstructionParserError(f"Undefined label: {label}")
                
            # Calculate relative branch offset in words (4 bytes per word)
            target_addr = self.symbol_table[label]
            current_addr = self.current_address + 4  # PC points to next instruction
            offset = (target_addr - current_addr) >> 2  # Divide by 4 to get word offset
            
            # Check if offset fits in 16 bits
            if not -32768 <= offset <= 32767:
                raise InstructionParserError(f"Branch offset too large: {offset}")
                
            immediate = offset & 0xFFFF
            
        else:  # ADDI
            if len(parts) != 4:
                raise InstructionParserError(f"Invalid I-type instruction format: {' '.join(parts)}")
                
            rt = self._parse_register(parts[1])
            rs = self._parse_register(parts[2])
            immediate = self._parse_immediate(parts[3])
        
        return (opcode << 26) | (rs << 21) | (rt << 16) | (immediate & 0xFFFF)
    
    def _parse_j_type(self, parts: List[str]) -> int:
        """Parse J-type instruction."""
        if len(parts) != 2:
            raise InstructionParserError(f"Invalid J-type instruction format: {' '.join(parts)}")
            
        opcode = self.J_TYPE_OPCODES[parts[0].upper()]
        label = parts[1].strip()
        
        # Get target address from symbol table
        if label not in self.symbol_table:
            raise InstructionParserError(f"Undefined label: {label}")
            
        target_addr = self.symbol_table[label]
        # Target address is word-aligned (lower 2 bits are 0)
        target = target_addr >> 2
        
        # Check if target fits in 26 bits
        if not 0 <= target < (1 << 26):
            raise InstructionParserError(f"Jump target too large: {hex(target_addr)}")
            
        return (opcode << 26) | (target & 0x3FFFFFF)
    
    def _parse_special_instruction(self, parts: List[str]) -> int:
        """Parse special instructions (HALT, CACHE)."""
        if len(parts) != 1:
            raise InstructionParserError(f"Invalid special instruction format: {' '.join(parts)}")
            
        opcode = self.SPECIAL_INSTRUCTIONS[parts[0].upper()]
        return (opcode << 26)  # Special instructions use only opcode
    
    def get_machine_code(self) -> bytes:
        """Get the generated machine code."""
        return bytes(self.machine_code)
    
    def _parse_immediate(self, imm_str: str) -> int:
        """Parse immediate value (decimal, hex, or binary)."""
        try:
            value = self._parse_number(imm_str)
            # Sign extend 16-bit immediate
            value = value & 0xFFFF
            if value & 0x8000:
                value |= -1 << 16
            return value
        except InstructionParserError:
            raise InstructionParserError(f"Invalid immediate value: {imm_str}")
    
    @staticmethod
    def _parse_register(reg_str: str) -> int:
        """Parse register string (e.g., '$1', '$ra') to number."""
        # Remove any trailing comma
        reg_str = reg_str.rstrip(',')
        
        if not reg_str.startswith('$'):
            raise InstructionParserError(f"Invalid register format: {reg_str}")
            
        reg_str = reg_str[1:]  # Remove '$'
        
        # Handle special register names
        special_regs = {
            'zero': 0, 'at': 1, 'v0': 2, 'v1': 3,
            'a0': 4, 'a1': 5, 'a2': 6, 'a3': 7,
            't0': 8, 't1': 9, 't2': 10, 't3': 11,
            't4': 12, 't5': 13, 't6': 14, 't7': 15,
            's0': 16, 's1': 17, 's2': 18, 's3': 19,
            's4': 20, 's5': 21, 's6': 22, 's7': 23,
            't8': 24, 't9': 25, 'k0': 26, 'k1': 27,
            'gp': 28, 'sp': 29, 'fp': 30, 'ra': 31
        }
        
        if reg_str in special_regs:
            return special_regs[reg_str]
            
        try:
            reg_num = int(reg_str)
            if 0 <= reg_num <= 31:
                return reg_num
            raise InstructionParserError(f"Register number out of range: {reg_str}")
        except ValueError:
            raise InstructionParserError(f"Invalid register: {reg_str}")
    
    @staticmethod
    def _parse_number(num_str: str) -> int:
        """Parse number in decimal, hex, or binary format."""
        num_str = num_str.strip().lower()
        
        try:
            if num_str.startswith('0x'):
                return int(num_str[2:], 16)
            elif num_str.startswith('0b'):
                return int(num_str[2:], 2)
            else:
                return int(num_str)
        except ValueError:
            raise InstructionParserError(f"Invalid number format: {num_str}")
