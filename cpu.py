"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes available for the RAM
        self.pc = 0 # program counter initialized at zero
        self.reg = [0] * 8 # register
        self.sp = 7 # set initial value of stack pointer 
        self.fl = [0] * 3

    # returning whatever the value is in the address
    def ram_read(self, MAR):
        return self.ram[MAR]

    # basically overwriting whatever address is in the ram with the new address
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue
                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number '{n}'")
                        sys.exit(1)

                    self.ram[address] = n
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            equal = self.fl[0]
            great = self.fl[1]
            less = self.fl[2]
            # greater than
            if reg_a > reg_b:
                equal = 0
                less = 0
                great = 1
            # less than 
            elif reg_a < reg_b:
                equal = 0
                less = 1
                great = 0
            # equal to each other
            elif reg_a == reg_b:
                equal = 1
                less = 0
                great = 0

            # sets the EGL flags to either 0 (false) or 1 (true)
            self.fl[:2] = [equal, great, less]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # local variables for the instructions
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010 
        
        # new sprint instructions
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        # operands
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        running = True

        while running:
            ir = self.ram_read(self.pc)

            if ir == LDI:
                # Set the value of a register to an integer.
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif ir == PRN:
                # Print numeric value stored in the given register.
                print(self.reg[operand_a])
                self.pc += 2

            elif ir == HLT:
                # exit the loop, basically HLT is going to be Python's exit() command
                running = False
                self.pc += 1

            elif ir == MUL:
                print(f"A: {operand_a}, B: {operand_b}")
                # multiply the operands calling the operation from alu
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3 # next instruction

            elif ir == CMP:
                self.alu('CMP', operand_a, operand_b)
                self.pc += 3

            elif ir == JMP:
                # jump to the address stored in the given register
                reg_jmp = operand_a
                add_jmp = self.reg[reg_jmp]
                # set the PC to the address stored in the given register.
                self.pc = add_jmp
            elif ir == JEQ:
                if self.fl[0] == 1:
                    # jump to the address stored in the given register
                    reg_jmp = operand_a
                    add_jmp = self.reg[reg_jmp]
                    # set the PC to the address stored in the given register.
                    self.pc = add_jmp
                else:
                    self.pc += 2
            elif ir == JNE:
                if self.fl[0] == 0:
                    # jump to the address stored in the given register
                    reg_jmp = operand_a
                    add_jmp = self.reg[reg_jmp]
                    # set the PC to the address stored in the given register.
                    self.pc = add_jmp
                else:
                    self.pc += 2
            else:
                print(f"Unknown Instruction {ir}")
                self.pc += 1

