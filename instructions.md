# Project overview
Design and implement a Python program that simulates the inner workings of a CPU, including functionality for a cache and memory bus. The simulator should fetch and execute instructions from an input file, handle memory initialization, and provide console output documenting the stages of instruction processing.

# Core features and functionalities
- Simulate CPU operations using a set of MIPS-like instructions.
- Implement classes for CPU, Cache, and Memory Bus.
- Fetch and parse instructions and memory initialization data from input f iles.
- Provide detailed console output for each stage of instruction processing.

Support the following instructions:
- Arithmetic operations: ADD, ADDI, SUB, SLT
- Branching: BNE, J, JAL
- Memory access: LW, SW
- Cache control: CACHE
- Program control: HALT

Technical Requirements:
-Use Python programming language.
-Implement object-oriented design principles.
-Use Git for version control.
-Develop locally using the command line for file navigation and execution.

Constraints:
-Must be a command-line application.
-Should be modular and maintainable.
-Ensure compatibility with Python 3.7 or above.

# Documentation
Unlikely that any external documentation is needed for this project.

# Current file structure
   ├── README.md
   ├── .gitignore
   ├── main.py
   ├── cpu.py
   ├── cache.py
   ├── memory_bus.py
   ├── instruction_parser.py
   ├── instruction_set.py
   ├── tests/
   │   └── test_cpu.py
   ├── inputs/
   │   ├── instructions.txt
   │   └── memory_init.txt
   └── docs/
       └── design.md

#Libraries
-Libraries/Modules: Optional (e.g., argparse for command-line arguments, logging for logging)


   cpu_simulator/
   ├── README.md
   ├── .gitignore
   ├── main.py
   ├── cpu.py
   ├── cache.py
   ├── memory_bus.py
   ├── instruction_parser.py
   ├── instruction_set.py
   ├── tests/
   │   └── test_cpu.py
   ├── inputs/
   │   ├── instructions.txt
   │   └── memory_init.txt
   └── docs/
       └── design.md


5. System Design
================

### 5.1 High-Level Architecture

The CPU Simulator will consist of the following components:

* CPU Class
	+ Handles instruction fetch, decode, and execute cycles
	+ Manages program counter (PC) and registers
* Cache Class
	+ Simulates cache memory behavior
	+ Implements cache on/off functionality and flushing
* Memory Bus Class
	+ Simulates main memory access
	+ Stores data and instructions
* Instruction Parser
	+ Reads and parses input files for instructions and memory initialization
* Instruction Set
	+ Defines the operations for each supported instruction

### 5.2 Class Definitions

#### CPU Class

* Attributes:
	+ Registers (e.g., R0 to R31)
	+ Program Counter (PC)
	+ Cache instance
	+ Memory Bus instance
	+ Execution flags
* Methods:
	+ fetch_instruction()
	+ decode_instruction()
	+ execute_instruction()
	+ update_pc()

#### Cache Class

* Attributes:
	+ Cache data storage
	+ Cache status (on/off)
* Methods:
	+ read(address)
	+ write(address, data)
	+ flush()
	+ toggle(status)

#### MemoryBus Class

* Attributes:
	+ Memory storage (e.g., a dictionary or list)
* Methods:
	+ load_memory(init_data)
	+ read(address)
	+ write(address, data)

#### InstructionParser Class/Module

* Methods:
	+ parse_instructions(file_path)
	+ parse_memory_init(file_path)

### 5.3 Instruction Set Architecture (ISA)

The CPU Simulator will support the following instructions:

* Arithmetic Instructions:
	+ ADD, ADDI, SUB, SLT
* Branch Instructions:
	+ BNE, J, JAL
* Memory Instructions:
	+ LW, SW
* Cache Control:
	+ CACHE
* Program Control:
	+ HALT

The instruction format will be as follows:

* R-Type: OPCODE Rd, Rs, Rt
* I-Type: OPCODE Rt, Rs, immediate
* J-Type: OPCODE target
* Memory Access: OPCODE Rt, offset(Rs)
* Cache Control: OPCODE code
* HALT: OPCODE

6. Implementation Plan
=======================

The project will be implemented in phases, focusing on one component at a time.

### 6.1 Input Parsing

* Objectives:
	+ Read instructions from instructions.txt
	+ Read memory initialization data from memory_init.txt
* Tasks:
	+ Implement InstructionParser to handle parsing
	+ Define the file formats and syntax rules
	+ Validate input data and handle errors
* Considerations:
	+ Decide on the format (e.g., one instruction per line)
	+ Support comments and blank lines in input files

### 6.2 Memory Bus Initialization

* Objectives:
	+ Initialize the MemoryBus with data from memory_init.txt
* Tasks:
	+ Implement MemoryBus.load_memory(init_data)
	+ Store data in an appropriate data structure (e.g., list or dict)
* Considerations:
	+ Addressing scheme (e.g., word-addressable, byte-addressable)
	+ Memory size limitations

### 6.3 CPU Instruction Execution

* Objectives:
	+ Implement instruction fetch, decode, and execute cycles
	+ Update the program counter and registers accordingly
* Tasks:
	+ Implement CPU methods: fetch_instruction(), decode_instruction(), execute_instruction()
	+ Handle each instruction type and its operands
	+ Implement the InstructionSet with methods or functions for each instruction
* Considerations:
	+ Instruction decoding logic
	+ Operand fetching from registers or immediate values
	+ Branch and jump execution flow
	+ Handling the HALT instruction to terminate execution

### 6.4 Cache Management

* Objectives:
	+ Implement cache functionality with on/off and flush capabilities
	+ Simulate cache read and write operations
* Tasks:
	+ Implement Cache class with read, write, flush, and toggle methods
	+ Integrate the cache with memory access in the CPU
	+ Handle the CACHE instruction codes
* Considerations:
	+ Decide on cache organization (e.g., direct-mapped, fully associative)
	+ Cache policies (e.g., write-through, write-back)
	+ Simulate cache hits and misses

### 6.5 Console Output and Logging

* Objectives:
	+ Provide detailed console output documenting each processing stage
	+ Optionally, implement logging to a file
* Tasks:
	+ Use print statements or the logging module
	+ Include outputs for:
		- Instruction fetch and decode steps
		- Register and memory state changes
		- Cache operations and status
		- Branch taken/not taken messages
		- Program termination message
* Considerations:
	+ Ensure the output is clear and informative
	+ Allow verbosity levels (e.g., verbose mode)

7. Testing and Debugging
=========================

### 7.1 Unit Testing

* Objectives:
	+ Verify that each component works correctly
	+ Ensure that the simulator executes instruction sequences as expected
* Tasks:
	+ Write unit tests for classes and methods using unittest or pytest
	+ Create test cases with known outputs
	+ Test error handling with invalid inputs
* Considerations:
	+ Continuous testing during development
	+ Use of assertions to validate states

8. Version Control with Git
==========================

### 8.1 Version Control

* Objectives:
	+ Track changes and maintain version history
	+ Collaborate effectively (if applicable)
* Tasks:
	+ Commit changes frequently with meaningful messages
	+ Use branches for new features or major changes
	+ Merge branches back into the main branch after testing
* Considerations:
	+ Tag releases or milestones
	+ Use GitHub or another remote repository service for backup and sharing

9. Documentation
===============

### 9.1 Code Documentation

* Objectives:
	+ Document code, usage instructions, and design decisions
	+ Provide a clear README for users and developers
* Tasks:
	+ Write docstrings for all classes and methods
	+ Update README.md with:
		- Project description
		- Installation and usage instructions
		- Examples of input files
		- Explanation of outputs
	+ Create a design document (design.md) detailing architecture and design choices
* Considerations:
	+ Use Markdown formatting for readability
	+ Include diagrams if helpful (e.g., class diagrams, flowcharts)