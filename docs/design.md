# CPU Simulator Design Document

## Overview
This document outlines the design and architecture of the CPU simulator.

## Components
- CPU: Handles instruction fetch, decode, and execute cycles
- Cache: Simulates cache memory behavior
- Memory Bus: Simulates main memory access
- Instruction Parser: Reads and parses input files
- Instruction Set: Defines supported operations

## Instruction Set Architecture
The CPU simulator supports the following instructions:
- Arithmetic: ADD, ADDI, SUB, SLT
- Branching: BNE, J, JAL
- Memory: LW, SW
- Cache Control: CACHE
- Program Control: HALT

## Implementation Details
### CPU Class
- Manages program counter and registers
- Implements fetch-decode-execute cycle

### Cache Class
- Simulates cache memory with on/off functionality
- Implements cache flushing

### Memory Bus Class
- Provides memory access interface
- Handles memory initialization

### Instruction Parser
- Parses instruction and memory initialization files
- Validates input format

### Testing Strategy
Unit tests are provided for each component to ensure correct functionality.
