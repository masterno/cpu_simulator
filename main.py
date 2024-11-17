#!/usr/bin/env python3
import argparse
from cpu import CPU
from instruction_parser import InstructionParser
from memory_bus import MemoryBus
from cache import Cache
from instruction_set import InstructionSet

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MIPS-like CPU Simulator')
    parser.add_argument('program', help='Assembly program file to execute')
    parser.add_argument('--memory-init', help='Memory initialization file')
    parser.add_argument('--num-fibonacci', type=int, default=10,
                       help='Number of Fibonacci numbers to calculate')
    args = parser.parse_args()
    
    # Initialize components
    memory_bus = MemoryBus()
    instruction_set = InstructionSet()
    cpu = CPU(memory_bus, instruction_set)
    instruction_parser = InstructionParser()
    
    try:
        # Load program into memory
        instruction_parser.parse_file(args.program)
        memory_bus.load_program(instruction_parser.get_machine_code(), 0)  # Load at address 0
        
        # Set up input value (number of Fibonacci numbers)
        memory_bus.io_devices[memory_bus.IO_BASE] = args.num_fibonacci
        
        # Load memory initialization data if provided
        if args.memory_init:
            memory_data = instruction_parser.parse_memory_init(args.memory_init)
            for addr, data in memory_data.items():
                memory_bus.write_word(addr, data)
        
        # Run the program
        print(f"\nExecuting program: {args.program}")
        print(f"Calculating {args.num_fibonacci} Fibonacci numbers...\n")
        
        cpu.run()
        
        # Print cache statistics
        stats = memory_bus.get_stats()
        cache_stats = stats['cache']
        print("\nCache Statistics:")
        print(f"Hits: {cache_stats['hits']}")
        print(f"Misses: {cache_stats['misses']}")
        print(f"Hit Rate: {cache_stats['hit_rate']:.2f}%")
        
        # Print final Fibonacci sequence
        print("\nFinal Fibonacci Sequence:")
        sequence = []
        for i in range(args.num_fibonacci):
            sequence.append(memory_bus.read_word(0x1000 + i * 4))
        print(sequence)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
