class IODevice:
    """Simple I/O device for the CPU simulator."""
    
    def __init__(self):
        """Initialize the I/O device with default values."""
        self.input_value = 10  # Default number of Fibonacci numbers to calculate
        self.output_buffer = []
        self.completion_status = 0
    
    def read(self, address: int) -> int:
        """Read from the I/O device.
        
        Args:
            address: The I/O address to read from
            
        Returns:
            The value read from the device
        """
        if address == 0xF0000000:  # Input device
            return self.input_value
        return 0
    
    def write(self, address: int, value: int) -> None:
        """Write to the I/O device.
        
        Args:
            address: The I/O address to write to
            value: The value to write
        """
        if address == 0xF0000004:  # Output device
            self.output_buffer.append(value)
            print(f"Fibonacci number generated: {value}")
        elif address == 0xF0000008:  # Completion status
            self.completion_status = value
            print(f"Program completed. Generated {value} Fibonacci numbers.")
    
    def set_input(self, value: int) -> None:
        """Set the input value for the device.
        
        Args:
            value: The number of Fibonacci numbers to calculate
        """
        self.input_value = value
    
    def get_output(self) -> list:
        """Get the output buffer contents.
        
        Returns:
            List of values written to the output device
        """
        return self.output_buffer.copy()
    
    def get_completion_status(self) -> int:
        """Get the completion status.
        
        Returns:
            The completion status value
        """
        return self.completion_status
