class MemoryBusError(Exception):
    """Custom exception for memory bus errors."""
    pass

class Cache:
    """Simple direct-mapped cache implementation."""
    
    def __init__(self, cache_size=1024, block_size=16):
        """Initialize cache with given size and block size."""
        self.cache_size = cache_size
        self.block_size = block_size
        self.cache = {}  # address -> value mapping
        self.hits = 0
        self.misses = 0
    
    def read_word(self, address: int) -> int:
        """Read a word from cache."""
        if address in self.cache:
            self.hits += 1
            return self.cache[address]
        self.misses += 1
        return None
    
    def write_word(self, address: int, value: int):
        """Write a word to cache."""
        self.cache[address] = value
    
    def get_stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class MemoryBus:
    """Memory bus that handles memory access and I/O devices."""
    
    MEMORY_SIZE = 0x100000  # 1MB of memory
    IO_BASE = 0xF0000000   # Base address for I/O devices
    
    def __init__(self):
        """Initialize memory bus with memory and I/O devices."""
        self.memory = bytearray(self.MEMORY_SIZE)
        self.cache = Cache()
        self.io_devices = {
            self.IO_BASE: 8,  # Input device (number of Fibonacci numbers)
            self.IO_BASE + 4: 0  # Output device
        }
        self.reads = 0
        self.writes = 0
        self.io_reads = 0
        self.io_writes = 0
    
    def register_io_device(self, address, device_type):
        """Register an I/O device at the specified address."""
        self.io_devices[address] = {"type": device_type, "value": 0}
    
    def _is_io_address(self, address):
        """Check if an address corresponds to an I/O device."""
        return address in self.io_devices
    
    def load_memory(self, init_data):
        """
        Load initial data into memory.
        
        Args:
            init_data: Dictionary mapping addresses to data values
        """
        try:
            for address, data in init_data.items():
                if not isinstance(data, (int, bytes, bytearray)):
                    raise MemoryBusError(f"Invalid data type at address {hex(address)}")
                    
                if isinstance(data, int):
                    # Convert integer to 4 bytes (32-bit)
                    data_bytes = data.to_bytes(4, byteorder='big')
                else:
                    data_bytes = data
                    
                if address + len(data_bytes) > self.MEMORY_SIZE:
                    raise MemoryBusError(f"Address {hex(address)} out of memory bounds")
                    
                self.memory[address:address + len(data_bytes)] = data_bytes
                
        except Exception as e:
            raise MemoryBusError(f"Error loading memory: {str(e)}")
    
    def load_program(self, program: bytes, base_address: int = 0) -> None:
        """
        Load program into memory at base address.
        
        Args:
            program: Program bytes to load
            base_address: Starting address to load program at
        """
        try:
            # Check program size
            if base_address + len(program) > self.MEMORY_SIZE:
                raise MemoryBusError("Program too large for memory")
                
            # Clear memory first
            for i in range(len(program)):
                self.memory[base_address + i] = program[i]
                
            # Invalidate cache
            self.cache.clear()
            
        except Exception as e:
            raise MemoryBusError(f"Error loading program: {str(e)}")
    
    def read_word(self, address: int) -> int:
        """Read a word from memory or I/O device."""
        if address >= self.IO_BASE:
            if address in self.io_devices:
                self.io_reads += 1
                return self.io_devices[address]
            raise MemoryError(f"Invalid I/O address: {hex(address)}")
        
        if address + 4 > self.MEMORY_SIZE:
            raise MemoryError(f"Memory read out of bounds: {hex(address)}")
        
        # Try to read from cache first
        value = self.cache.read_word(address)
        if value is not None:
            return value
        
        # Cache miss, read from memory
        value = int.from_bytes(self.memory[address:address + 4], byteorder='big')
        self.cache.write_word(address, value)
        self.reads += 1
        return value
        
    def write_word(self, address: int, value: int):
        """Write a word to memory or I/O device."""
        if address >= self.IO_BASE:
            if address in self.io_devices:
                self.io_devices[address] = value
                self.io_writes += 1
                return
            raise MemoryError(f"Invalid I/O address: {hex(address)}")
        
        if address + 4 > self.MEMORY_SIZE:
            raise MemoryError(f"Memory write out of bounds: {hex(address)}")
        
        # Write to cache
        self.cache.write_word(address, value)
        
        # Write to memory
        self.memory[address:address + 4] = value.to_bytes(4, byteorder='big')
        self.writes += 1
    
    def read(self, address):
        """
        Read a word (4 bytes) from memory or I/O device.
        
        Args:
            address: Memory address to read from
            
        Returns:
            32-bit integer value
        """
        # Check for I/O access
        if address >= self.IO_BASE:
            if address in self.io_devices:
                return self.io_devices[address]
            raise MemoryError(f"Invalid I/O address: {hex(address)}")
            
        # Check address bounds
        if not (0 <= address < self.MEMORY_SIZE - 3):
            raise MemoryError(f"Memory read out of bounds: {hex(address)}")
            
        # Check if word is in cache
        word = self.cache.read_word(address)
        if word is not None:
            return word
            
        # Word not in cache, read from memory
        word = int.from_bytes(self.memory[address:address + 4], byteorder='big')
        self.reads += 1
        return word
    
    def write(self, address, data):
        """
        Write a word (4 bytes) to memory or I/O device.
        
        Args:
            address: Memory address to write to
            data: 32-bit integer value to write
        """
        # Check for I/O access
        if address >= self.IO_BASE:
            if address in self.io_devices:
                self.io_devices[address] = data
                self.io_writes += 1
                return
            raise MemoryError(f"Invalid I/O address: {hex(address)}")
            
        # Check address bounds
        if not (0 <= address < self.MEMORY_SIZE - 3):
            raise MemoryError(f"Memory write out of bounds: {hex(address)}")
            
        # Update cache
        self.cache.write_word(address, data)
        
        # Write to memory
        data_bytes = data.to_bytes(4, byteorder='big')
        self.memory[address:address + 4] = data_bytes
        self.writes += 1
    
    def _read_io(self, address):
        """Read from I/O device."""
        if address not in self.io_devices:
            raise MemoryError(f"Invalid I/O device address: {hex(address)}")
            
        device = self.io_devices[address]
        if device["type"] != "input":
            raise MemoryError(f"Cannot read from output device at {hex(address)}")
            
        self.io_reads += 1
        return device["value"]
        
    def _write_io(self, address, value):
        """Write to I/O device."""
        if address not in self.io_devices:
            raise MemoryError(f"Invalid I/O device address: {hex(address)}")
            
        device = self.io_devices[address]
        if device["type"] != "output":
            raise MemoryError(f"Cannot write to input device at {hex(address)}")
            
        self.io_writes += 1
        device["value"] = value
    
    def _find_io_device(self, address):
        """Find the I/O device mapped to the given address."""
        for start_addr, info in self.io_devices.items():
            if start_addr <= address < start_addr + 4:
                return info
        return None
    
    def _check_bounds(self, address: int) -> None:
        """Check if address is within memory bounds."""
        if address < 0 or address >= self.MEMORY_SIZE:
            # Check if this is an I/O device address
            if address in self.io_devices:
                return
            # Stop execution immediately on first out-of-bounds access
            raise MemoryError(f"Memory access out of bounds at address {hex(address)}")
    
    def get_stats(self):
        """Get memory bus statistics."""
        cache_stats = self.cache.get_stats()
        return {
            'cache': cache_stats,
            'memory_reads': self.reads,
            'memory_writes': self.writes,
            'io_reads': self.io_reads,
            'io_writes': self.io_writes
        }
    
    def clear(self):
        """Clear memory bus state."""
        self.memory = bytearray(self.MEMORY_SIZE)
        self.cache.clear()
        self.reads = 0
        self.writes = 0
        self.io_reads = 0
        self.io_writes = 0
    
    def dump_memory(self, start_addr, size):
        """
        Dump a section of memory for debugging.
        
        Args:
            start_addr: Starting address
            size: Number of bytes to dump
            
        Returns:
            Bytes object containing the memory contents
        """
        if start_addr + size > self.MEMORY_SIZE:
            raise MemoryBusError("Memory dump range out of bounds")
            
        return bytes(self.memory[start_addr:start_addr + size])
