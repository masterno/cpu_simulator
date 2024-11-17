import unittest
from cpu import CPU
from cache import Cache
from memory_bus import MemoryBus

class TestCPU(unittest.TestCase):
    def setUp(self):
        self.memory_bus = MemoryBus()
        self.cache = Cache()
        self.cpu = CPU(self.cache, self.memory_bus)
    
    def test_initialization(self):
        self.assertEqual(len(self.cpu.registers), 32)
        self.assertEqual(self.cpu.pc, 0)
