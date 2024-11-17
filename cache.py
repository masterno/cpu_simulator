class CacheError(Exception):
    """Custom exception for cache errors."""
    pass

class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = None
        self.data = None
        self.last_accessed = 0

class Cache:
    def __init__(self, memory_bus, cache_size=1024, line_size=32):
        """
        Initialize the cache with specified parameters.
        
        Args:
            memory_bus: Reference to the memory bus for data access
            cache_size: Total cache size in bytes (default 1024)
            line_size: Cache line size in bytes (default 32)
        """
        self.memory_bus = memory_bus
        self.enabled = True
        self.access_count = 0
        
        # Cache configuration
        self.cache_size = cache_size
        self.line_size = line_size
        self.num_lines = cache_size // line_size
        
        # Calculate address bit fields
        self.offset_bits = self._log2(line_size)
        self.index_bits = self._log2(self.num_lines)
        self.tag_bits = 32 - (self.offset_bits + self.index_bits)
        
        # Initialize cache lines
        self.lines = [CacheLine() for _ in range(self.num_lines)]
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def read(self, address):
        """
        Read data from cache.
        
        Args:
            address: Memory address to read from
            
        Returns:
            Data at the specified address
        """
        if not self.enabled:
            return self.memory_bus.read(address)
            
        self.access_count += 1
        
        # Extract address fields
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        
        cache_line = self.lines[index]
        
        # Cache hit
        if cache_line.valid and cache_line.tag == tag:
            self.hits += 1
            cache_line.last_accessed = self.access_count
            return cache_line.data[offset:offset + 4]  # Return 4 bytes (word)
            
        # Cache miss
        self.misses += 1
        
        # Read entire cache line from memory
        line_address = address & ~((1 << self.offset_bits) - 1)
        data = []
        for i in range(self.line_size):
            data.append(self.memory_bus.read(line_address + i))
            
        # Update cache line
        cache_line.valid = True
        cache_line.tag = tag
        cache_line.data = data
        cache_line.last_accessed = self.access_count
        
        return cache_line.data[offset:offset + 4]  # Return requested word
    
    def write(self, address, data):
        """
        Write data to cache (write-through policy).
        
        Args:
            address: Memory address to write to
            data: Data to write
        """
        if not self.enabled:
            self.memory_bus.write(address, data)
            return
            
        self.access_count += 1
        
        # Extract address fields
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        
        cache_line = self.lines[index]
        
        # Update memory (write-through)
        self.memory_bus.write(address, data)
        
        # Update cache if it's a hit
        if cache_line.valid and cache_line.tag == tag:
            self.hits += 1
            cache_line.data[offset:offset + 4] = data
            cache_line.last_accessed = self.access_count
        else:
            self.misses += 1
            # On write miss, we could either allocate or not (write-no-allocate)
            # Here we implement write-no-allocate for simplicity
    
    def flush(self):
        """Flush the entire cache."""
        for line in self.lines:
            line.valid = False
            line.tag = None
            line.data = None
        self.hits = 0
        self.misses = 0
        self.access_count = 0
    
    def toggle(self, status):
        """Enable or disable the cache."""
        self.enabled = status
        if not status:
            self.flush()
    
    def get_stats(self):
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary containing hit rate and miss rate
        """
        total_accesses = self.hits + self.misses
        if total_accesses == 0:
            return {'hit_rate': 0, 'miss_rate': 0}
            
        hit_rate = self.hits / total_accesses
        miss_rate = self.misses / total_accesses
        
        return {
            'hit_rate': hit_rate,
            'miss_rate': miss_rate,
            'total_accesses': total_accesses,
            'hits': self.hits,
            'misses': self.misses
        }
    
    @staticmethod
    def _log2(x):
        """Calculate the log base 2 of a number (for bit field calculations)."""
        n = 0
        while x > 1:
            x >>= 1
            n += 1
        return n

class Cache:
    """Direct-mapped cache implementation."""
    
    def __init__(self, memory_bus, size=1024):
        """
        Initialize the cache.
        
        Args:
            memory_bus: Reference to the memory bus
            size: Cache size in bytes (default 1KB)
        """
        self.memory_bus = memory_bus
        self.size = size
        self.line_size = 32  # 32-byte cache lines
        self.num_lines = size // self.line_size
        
        # Cache storage: each entry is (valid, tag, data)
        self.lines = [(False, 0, bytearray(self.line_size)) for _ in range(self.num_lines)]
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def read_word(self, address):
        """
        Read a word from cache or memory.
        
        Args:
            address: Memory address to read from
            
        Returns:
            32-bit word value
        """
        # Handle I/O space directly through memory bus
        if address >= self.memory_bus.IO_START:
            return self.memory_bus.read_word(address)
        
        # Calculate cache line index and tag
        line_index = (address // self.line_size) % self.num_lines
        tag = address // (self.line_size * self.num_lines)
        offset = address % self.line_size
        
        # Check for cache hit
        valid, line_tag, data = self.lines[line_index]
        if valid and line_tag == tag:
            self.hits += 1
            return int.from_bytes(data[offset:offset + 4], byteorder='big')
        
        # Cache miss: load line from memory
        self.misses += 1
        line_addr = (address // self.line_size) * self.line_size
        
        # Read entire cache line from memory
        for i in range(0, self.line_size, 4):
            word = self.memory_bus.read_word(line_addr + i)
            data[i:i + 4] = word.to_bytes(4, byteorder='big')
        
        # Update cache line
        self.lines[line_index] = (True, tag, data)
        
        # Return requested word
        return int.from_bytes(data[offset:offset + 4], byteorder='big')
    
    def write_word(self, address, value):
        """
        Write a word to cache and memory (write-through).
        
        Args:
            address: Memory address to write to
            value: 32-bit word value to write
        """
        # Handle I/O space directly through memory bus
        if address >= self.memory_bus.IO_START:
            self.memory_bus.write_word(address, value)
            return
        
        # Write to memory (write-through)
        self.memory_bus.write_word(address, value)
        
        # Calculate cache line index and tag
        line_index = (address // self.line_size) % self.num_lines
        tag = address // (self.line_size * self.num_lines)
        offset = address % self.line_size
        
        # Check for cache hit
        valid, line_tag, data = self.lines[line_index]
        if valid and line_tag == tag:
            self.hits += 1
            # Update cache line
            data[offset:offset + 4] = value.to_bytes(4, byteorder='big')
            self.lines[line_index] = (True, tag, data)
        else:
            # Cache miss: write-no-allocate policy
            self.misses += 1
    
    def invalidate(self, address=None):
        """
        Invalidate cache line(s).
        
        Args:
            address: If provided, invalidate only the line containing this address
        """
        if address is None:
            # Invalidate entire cache
            for i in range(self.num_lines):
                self.lines[i] = (False, 0, bytearray(self.line_size))
        else:
            # Invalidate specific line
            line_index = (address // self.line_size) % self.num_lines
            self.lines[line_index] = (False, 0, bytearray(self.line_size))
    
    def get_hits(self):
        """Get the number of cache hits."""
        return self.hits
    
    def get_misses(self):
        """Get the number of cache misses."""
        return self.misses
    
    def get_hit_rate(self):
        """Get the cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0
