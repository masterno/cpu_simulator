# Calculate Fibonacci sequence with overflow protection
# Input: Number of Fibonacci numbers to calculate (stored at 0x0)
# Output: Fibonacci sequence stored in memory starting at 0x1000
# Note: Program will stop if next number would exceed 32-bit signed int max

# Initialize memory pointers and counters
ADDI $s1, $zero, 0x1000    # Base address for output
ADDI $t4, $s1, 0           # Current output address
LW   $s0, 0($zero)         # Load number of Fibonacci numbers to calculate

# Initialize first two Fibonacci numbers
ADDI $t0, $zero, 1         # First number (F0 = 1)
SW   $t0, 0($t4)           # Store F0
ADDI $t4, $t4, 4           # Increment address

ADDI $t1, $zero, 1         # Second number (F1 = 1)
SW   $t1, 0($t4)           # Store F1
ADDI $t4, $t4, 4           # Increment address

# Initialize loop counter and max value
ADDI $t3, $zero, 2         # Already stored 2 numbers
ADDI $s2, $zero, 0x4000    # Load a safe maximum value that won't overflow

loop:
    # Check if we've calculated enough numbers
    BEQ  $t3, $s0, done    # If counter equals target, exit
    
    # Check if next addition would overflow
    SUB  $s3, $s2, $t1     # MAX - current number
    BEQ  $s3, $zero, done  # If difference is 0, we're at max
    BNE  $s3, $s2, safe    # If difference != MAX, we haven't overflowed
    J    done              # Otherwise, stop to prevent overflow
    
safe:
    # Calculate next Fibonacci number
    ADD  $t2, $t1, $t0     # t2 = F_n-1 + F_n-2
    
    # Store result
    SW   $t2, 0($t4)       # Store F_n
    ADDI $t4, $t4, 4       # Increment pointer
    
    # Update previous values
    ADD  $t0, $zero, $t1   # t0 = F_n-1
    ADD  $t1, $zero, $t2   # t1 = F_n
    
    # Increment counter
    ADDI $t3, $t3, 1
    
    # Continue loop
    J    loop

done:
    HALT
