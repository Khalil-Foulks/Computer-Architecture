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
MUL = 0b10100010
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0 # program counter, pointer to the currently executing instruction
        self.ram = [0] * 256 # memory; 256 bits/slots 
        self.reg = [0] * 8 # register
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add
        self.sp = 0b00000111 # stack pointer set to 7
        self.reg[self.sp] = 0xf4 # setting register 7 to hex value of F4
    
    def ram_read(self, address):
        value_in_mem = self.ram[address]

        return value_in_mem
        
    def ram_write(self, address, value):
        self.ram[address] = value


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
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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
    
    def handle_hlt(self, operand_a, operand_b):
        sys.exit()

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self,  operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def handle_mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3
    
    def handle_add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3
    
    def push_val(self, value):
        # Decrement the SP
        self.reg[self.sp] -= 1 

        # Copy the value onto the stack
        top_of_stack = self.reg[self.sp]
        self.ram[top_of_stack] = value

    def pop_val(self):
        # Get value from top of stack
        top_of_stack = self.reg[self.sp]
        # copy of value from top of stack
        value = self.ram[top_of_stack]
        # Increment the SP
        self.reg[self.sp] += 1

        return value
        
    def handle_pop(self, operand_a, operand_b):
        # self.trace()

        # Store in a register
        reg_num = operand_a
        self.reg[reg_num] = self.pop_val()

        self.pc += 2

    def handle_push(self, operand_a, operand_b):
        # self.trace() 

        # Grab the value out of the given register
        reg_num = operand_a
        value = self.reg[reg_num]

        self.push_val(value)

        self.pc += 2
    
    
    def handle_call(self, operand_a, operand_b):
        # Get address of the next instruction after the CALL
        return_addr = self.pc + 2
        
        # push on to the stack
        self.push_val(return_addr)

        # Grab the subroutine address
        reg_num = operand_a
        subroutine = self.reg[reg_num]

        # Jump to subroutine
        self.pc = subroutine

    def handle_ret(self, operand_a, operand_b):
        # Get return addr from top of stack
        return_value = self.pop_val()

        # Store it in the PC
        self.pc = return_value

    def run(self):
        """Run the CPU."""
        running = True
        
        while running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # if current opcode is in dictionary
            if self.branchtable.get(ir):
                # run the associated function passing in operand_a and operand_b
                self.branchtable[ir](operand_a, operand_b)
            else:
                print(f"unknown instruction {ir} at address {self.pc}")
                sys.exit(1)

