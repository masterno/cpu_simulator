# CPU Simulator

A Python-based CPU simulator that implements a MIPS-like instruction set architecture.

## Features
- Simulates basic CPU operations
- Implements cache functionality
- Supports various instructions including arithmetic, branching, and memory operations
- Provides detailed console output for instruction processing stages

## Requirements
- Python 3.7 or above

## Project Structure
```
├── README.md
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
```

## Setup
1. Ensure Python 3.7+ is installed
2. Clone the repository
3. Run `python main.py`

## Usage
1. Create an instruction file in `inputs/instructions.txt`
2. Create a memory initialization file in `inputs/memory_init.txt`
3. Run the simulator: `python main.py`

## Testing
Run the tests using:
```bash
python -m unittest tests/test_cpu.py
```

## Documentation
See `docs/design.md` for detailed design documentation.
