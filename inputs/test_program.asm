# Test program to sum numbers in memory
# Numbers are stored at addresses 0x100-0x10C
# Result will be stored in $t0

    # Initialize registers
    ADDI $t0, $zero, 0      # sum = 0
    ADDI $t1, $zero, 0x100  # address = 0x100
    ADDI $t2, $zero, 4      # count = 4

loop:
    LW   $t3, 0($t1)        # Load word from memory
    ADD  $t0, $t0, $t3      # sum += number
    ADDI $t1, $t1, 4        # address += 4
    ADDI $t2, $t2, -1       # count--
    BNE  $t2, $zero, loop   # if count != 0 goto loop
    
    # Store result
    SW   $t0, 0x200($zero)  # Store sum at 0x200
    HALT                     # End program
