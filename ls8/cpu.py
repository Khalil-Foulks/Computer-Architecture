"""CPU functionality."""

import sys

NOP = 0b00000000
HLT = 0b00000001 
LDI = 0b10000010
LD = 0b10000011 
ST = 0b10000100 
POP = 0b01000110 
PRN = 0b01000111 
PRA = 0b01001000 
PUSH = 0b01000101 

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0 # program counter, pointer to the currently executing instruction
        self.ram = [0] * 256 # memory; 256 bits/slots 
        self.reg = [0] * 8 # register
    
    def ram_read(self, address):
        value_in_mem = self.ram[address]

        return value_in_mem
        
    def ram_write(self, address, value):
        self.ram[address] = value
        return self.ram[address]


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000, # operand
        #     0b00001000, # operand
        #     0b01000111, # PRN R0
        #     0b00000000, # operand
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        #----------------------------------------------
        if len(sys.argv) != 2:
            print("usage: comp.py progname")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    # print(line)
                    # skip blank lines or comments
                    if line == '' or line[0] == "#":
                        continue

                    try:
                    	str_value = line.split("#")[0]
                        # converts binary string from base 2 to int
                    	value = int(str_value, 2)

                    except ValueError:
                    	print(f"Invalid number: {str_value}")
                    	sys.exit(1)

                    self.ram[address] = value
                    address += 1

        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)



    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
        running = True
        
        while running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            # self.trace()

            if ir == HLT:
                running = False
                self.pc += 1

            elif ir == PRN:
                print(self.ram_read(operand_a))
                self.pc += 2

            elif ir == LDI:
                self.ram_write(operand_a, operand_b)
                self.pc += 3

            else:
                print(f"unknown instruction {ir} at address {self.pc}")
                sys.exit(1)

