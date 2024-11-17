import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from instruction_parser import InstructionParser, InstructionParserError

class TestInstructionParser(unittest.TestCase):
    def setUp(self):
        self.parser = InstructionParser()
        self.test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs')
        self.test_program = os.path.join(self.test_dir, 'test_program.asm')
        self.test_memory = os.path.join(self.test_dir, 'memory_init.txt')

    def test_parse_instructions(self):
        """Test parsing of assembly instructions."""
        instructions = self.parser.parse_instructions(self.test_program)
        
        # Verify we got the expected number of instructions
        self.assertEqual(len(instructions), 9)  # 8 instructions + HALT
        
        # Verify first instruction (ADDI $t0, $zero, 0)
        self.assertEqual(instructions[0], 0x20080000)  # opcode=8, rt=8, rs=0, imm=0
        
        # Verify memory load instruction (LW $t3, 0($t1))
        self.assertEqual(instructions[3], 0x8D2B0000)  # opcode=23, rt=11, rs=9, imm=0
        
        # Verify branch instruction (BNE $t2, $zero, loop)
        self.assertEqual(instructions[7] >> 26, 0x5)  # opcode=5 (BNE)

    def test_parse_memory_init(self):
        """Test parsing of memory initialization file."""
        memory_data = self.parser.parse_memory_init(self.test_memory)
        
        # Verify memory contents
        self.assertEqual(memory_data[0x100], 10)
        self.assertEqual(memory_data[0x104], 20)
        self.assertEqual(memory_data[0x108], 30)
        self.assertEqual(memory_data[0x10C], 40)
        self.assertEqual(memory_data[0x200], 0)

    def test_invalid_instruction(self):
        """Test handling of invalid instructions."""
        with self.assertRaises(InstructionParserError):
            self.parser._parse_instruction("INVALID $t0, $t1, $t2")

    def test_invalid_register(self):
        """Test handling of invalid register names."""
        with self.assertRaises(InstructionParserError):
            self.parser._parse_register("invalid")
        with self.assertRaises(InstructionParserError):
            self.parser._parse_register("$32")  # Out of range

    def test_number_parsing(self):
        """Test parsing of numbers in different formats."""
        self.assertEqual(self.parser._parse_number("42"), 42)
        self.assertEqual(self.parser._parse_number("0x2A"), 42)
        self.assertEqual(self.parser._parse_number("0b101010"), 42)
        with self.assertRaises(InstructionParserError):
            self.parser._parse_number("invalid")

if __name__ == '__main__':
    unittest.main()
