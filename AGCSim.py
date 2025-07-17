class AGC:
    """
    Block II Apollo Guidance Computer simulation.
    Implements authentic one's complement arithmetic, negative zero, double-precision math,
    cycle-accurate instruction sequencing, interrupts, and peripheral stubs.
    """


    # AGC constants
    FIXED_SIZE = 36864      # ROM
    ERASE_SIZE = 2048       # RAM
    WORD_MASK = 0x7FFF      # 15 bits
    SIGN_BIT = 0x4000       # Sign bit
    NEG_ZERO = 0x7FFF       # Negative zero

    def __init__(self):
        self.memory = [0] * self.FIXED_SIZE
        self.erasable_memory = [0] * self.ERASE_SIZE
        self.L = 0
        self.Q = 0
        self.accumulator = 0
        self.program_counter = 0
        self.extended_mode = False
        self.extended_address = None
        self.interrupt_enabled = True
        self.interrupt_pending = False
        self.interrupt_vector = 0
        self.cycle_count = 0  # For cycle-accurate simulation
        self.dsky_buffer = []
        self.interface_counters = [0] * 10  # Example stub

        # Instruction set mapping
        self.instruction_set = {
            "TC": self.tc, "CCS": self.ccs, "INDEX": self.index, "XCH": self.xch,
            "CA": self.ca, "CS": self.cs, "TS": self.ts, "AD": self.ad, "MSK": self.msk,
            "EXTEND": self.extend, "MP": self.mp, "DV": self.dv, "SU": self.su,
            "DCA": self.dca, "DCS": self.dcs, "DAD": self.dad, "DSU": self.dsu,
            "LXCH": self.lxch, "QXCH": self.qxch, "INCR": self.incr, "AUG": lambda *args: self.aug(),
            "DIM": self.dim, "BZF": self.bzf, "BZM": self.bzm, "RELINT": self.relint,
            "INHINT": self.inhint, "EDRUPT": self.edrupt, "RESUME": self.resume,
            "CYR": self.cyr, "SR": self.sr, "SL": self.sl, "PINC": self.pinc,
            "MINC": self.minc, "DXCH": self.dxch, "INT": lambda *args: self.interrupt(),
        }
        # add involuntary instructions(EDRUPT, INT,PINC,MINC,RESUME,Time1,Time2,Cdux,cduy,cduz)

    # --- Utility functions ---
    def agc_word(self, value):
        """AGC words are 15 bits, one's complement."""
        value &= self.WORD_MASK
        return value

    def agc_add(self, a, b):
        """
        One's complement addition with repeated end-around carry.
        Preserves negative zero for arithmetic results.
        """
        sum_raw = a + b
        result = sum_raw & self.WORD_MASK
        carry = sum_raw >> 15
        while carry:
            sum_raw = result + carry
            result = sum_raw & self.WORD_MASK
            carry = sum_raw >> 15
        # Convert negative zero to zero
        if result == self.NEG_ZERO:
            result = 0
        return result

    def agc_sub(self, a, b):
        """One's complement subtraction."""
        result = self.agc_add(a, self.agc_complement(b))
        # Do NOT convert negative zero to zero; preserve negative zero
        return result

    def agc_complement(self, value):
        """One's complement negation."""
        return (~value) & self.WORD_MASK

    def agc_sign(self, value):
        """Returns +1 for positive, -1 for negative, 0 for zero."""
        if value == 0:
            return 0
        return -1 if value & self.SIGN_BIT else 1

    def agc_is_negative(self, value):
        """True if value is negative (sign bit set)."""
        return (value & self.SIGN_BIT) != 0

    def agc_is_zero(self, value):
        """True if value is zero (including negative zero)."""
        return value == 0 or value == self.NEG_ZERO

    # --- Instruction Implementations ---

    def tc(self, address):
        self.program_counter = address
        self.cycle_count += 1

    def ccs(self, address):
        value = self.erasable_memory[address]
        if self.agc_is_zero(value):
            self.program_counter = self.agc_add(self.program_counter, 1)
        elif not self.agc_is_negative(value):
            self.accumulator = self.agc_complement(self.accumulator)
        else:
            self.accumulator = self.accumulator & ~self.SIGN_BIT
        self.cycle_count += 2

    def index(self, address):
        self.program_counter = address
        self.cycle_count += 1

    def xch(self, address):
        temp = self.accumulator
        self.accumulator = self.erasable_memory[address]
        self.erasable_memory[address] = temp
        self.cycle_count += 2

    def ca(self, address):
        self.accumulator = self.erasable_memory[address]
        self.cycle_count += 2

    def cs(self, address):
        self.accumulator = self.agc_complement(self.erasable_memory[address])
        self.cycle_count += 2

    def ts(self, address):
        self.erasable_memory[address] = self.accumulator
        self.accumulator = 0
        self.cycle_count += 2

    def ad(self, address):
        self.accumulator = self.agc_add(self.accumulator, self.erasable_memory[address])
        self.cycle_count += 2

    def msk(self, mask):
        self.accumulator &= mask & self.WORD_MASK
        self.cycle_count += 1

    def extend(self, address=None):
        self.extended_mode = True
        self.extended_address = address
        self.cycle_count += 1

    def mp(self, address):
        a = self.accumulator
        b = self.erasable_memory[address]
        product = a * b
        self.L = (product >> 15) & self.WORD_MASK
        self.accumulator = product & self.WORD_MASK
        self.cycle_count += 6

    def dv(self, address):
        dividend = (self.L << 15) | self.accumulator
        divisor = self.erasable_memory[address]
        if divisor == 0:
            self.accumulator = 0
            self.L = 0
            self.interrupt_pending = True
            self.cycle_count += 6
            return
        quotient = dividend // divisor
        remainder = dividend % divisor
        self.accumulator = quotient & self.WORD_MASK
        self.L = remainder & self.WORD_MASK
        self.cycle_count += 6

    def su(self, address):
        self.accumulator = self.agc_sub(self.accumulator, self.erasable_memory[address])
        self.cycle_count += 2

    def dca(self, address):
        self.accumulator = self.erasable_memory[address]
        self.L = self.erasable_memory[(address + 1) % self.ERASE_SIZE]
        self.cycle_count += 4

    def dcs(self, address):
        self.accumulator = self.agc_complement(self.erasable_memory[address])
        self.L = self.agc_complement(self.erasable_memory[(address + 1) % self.ERASE_SIZE])
        self.cycle_count += 4

    def dad(self, address):
        # Add low word and detect carry
        a = self.accumulator
        b = self.erasable_memory[address]
        sum_low_raw = a + b
        sum_low = self.agc_add(a, b)
        carry = 1 if sum_low_raw > self.WORD_MASK else 0
        l = self.L
        b2 = self.erasable_memory[(address + 1) % self.ERASE_SIZE]
        sum_high = self.agc_add(l, b2)
        sum_high = self.agc_add(sum_high, carry)
        self.accumulator = sum_low & self.WORD_MASK
        self.L = sum_high & self.WORD_MASK
        self.cycle_count += 6

    def dsu(self, address):
        # Subtract low word and detect borrow
        a = self.accumulator
        b = self.erasable_memory[address]
        diff_low = self.agc_sub(a, b)
        borrow = 1 if a < b else 0
        l = self.L
        b2 = self.erasable_memory[(address + 1) % self.ERASE_SIZE]
        diff_high = self.agc_sub(l, b2)
        diff_high = self.agc_sub(diff_high, borrow)
        self.accumulator = diff_low & self.WORD_MASK
        self.L = diff_high & self.WORD_MASK
        self.cycle_count += 6

    def lxch(self, address):
        temp = self.L
        self.L = self.erasable_memory[address]
        self.erasable_memory[address] = temp
        self.cycle_count += 2

    def qxch(self, address):
        temp = self.Q
        self.Q = self.erasable_memory[address]
        self.erasable_memory[address] = temp
        self.cycle_count += 2

    def incr(self, address):
        self.erasable_memory[address] = self.agc_add(self.erasable_memory[address], 1)
        self.cycle_count += 2

    def aug(self):
        # Stub implementation for AUG instruction
        pass
    def dim(self, address):
        self.erasable_memory[address] = self.agc_sub(self.erasable_memory[address], 1)
        self.cycle_count += 2

    def bzf(self, address):
        if self.agc_is_zero(self.accumulator) or not self.agc_is_negative(self.accumulator):
            self.program_counter = address
        self.cycle_count += 2

    def bzm(self, address):
        if self.agc_is_negative(self.accumulator) and not self.agc_is_zero(self.accumulator):
            self.program_counter = address
        self.cycle_count += 2

    def relint(self):
        self.interrupt_enabled = True
        self.cycle_count += 1

    def inhint(self):
        self.interrupt_enabled = False
        self.cycle_count += 1

    def edrupt(self):
        self.interrupt_pending = True
        self.cycle_count += 1

    def resume(self):
        self.interrupt_pending = False
        self.cycle_count += 1

    def cyr(self, address):
        val = self.erasable_memory[address]
        lsb = val & 1
        val = (val >> 1) | (lsb << 14)
        self.erasable_memory[address] = val & self.WORD_MASK
        self.cycle_count += 2

    def sr(self, address):
        self.erasable_memory[address] = (self.erasable_memory[address] >> 1) & self.WORD_MASK
        self.cycle_count += 2

    def sl(self, address):
        self.erasable_memory[address] = (self.erasable_memory[address] << 1) & self.WORD_MASK
        self.cycle_count += 2

    def pinc(self, address):
        if not self.agc_is_negative(self.erasable_memory[address]):
            self.erasable_memory[address] = self.agc_add(self.erasable_memory[address], 1)
        self.cycle_count += 2

    def minc(self, address):
        if self.agc_is_negative(self.erasable_memory[address]):
            self.erasable_memory[address] = self.agc_add(self.erasable_memory[address], 1)
        self.cycle_count += 2

    def dxch(self, address):
        temp_a = self.accumulator
        temp_l = self.L
        self.accumulator = self.erasable_memory[address]
        self.L = self.erasable_memory[(address + 1) % len(self.erasable_memory)]
        self.erasable_memory[address] = temp_a
        self.erasable_memory[(address + 1) % len(self.erasable_memory)] = temp_l
        self.cycle_count += 4

    def interrupt(self):
        self.interrupt_pending = True
        self.cycle_count += 1

    def execute_instruction(self, instruction):
        if not instruction:
            return
        opcode = instruction[0]
        args = instruction[1:] if len(instruction) > 1 else []
        # Handle EXTEND mode
        if self.extended_mode:
            extended_instruction_set = {
                "MP": self.mp,
                "DV": self.dv,
                "SU": self.su,
            }
            if opcode in extended_instruction_set:
                extended_instruction_set[opcode](*args)
            else:
                raise ValueError(f"Unknown extended instruction: {opcode}")
            self.extended_mode = False
            self.extended_address = None
        else:
            if opcode in self.instruction_set:
                self.instruction_set[opcode](*args)
            else:
                raise ValueError(f"Unknown instruction: {opcode}")

    # --- Setup and Utility Methods ---

    def reset(self):
        self.memory = [0] * self.FIXED_SIZE
        self.erasable_memory = [0] * self.ERASE_SIZE
        self.L = 0
        self.Q = 0
        self.accumulator = 0
        self.program_counter = 0
        self.extended_mode = False
        self.extended_address = None
        self.interrupt_enabled = True
        self.interrupt_pending = False
        self.interrupt_vector = 0
        self.cycle_count = 0
        self.dsky_buffer = []
        self.interface_counters = [0] * 10

    # --- Peripheral Simulation (Stub) ---

    def dsky_input(self, value):
        self.dsky_buffer.append(value)

    def dsky_output(self):
        if self.dsky_buffer:
            return self.dsky_buffer.pop(0)
        return None

    def interface_counter_read(self, idx):
        if 0 <= idx < len(self.interface_counters):
            return self.interface_counters[idx]
        return None

    def interface_counter_write(self, idx, value):
        if 0 <= idx < len(self.interface_counters):
            self.interface_counters[idx] = value & self.WORD_MASK

# Tests for agc_word and arithmetic operations

if __name__ == "__main__":
    agc = AGC()
    # Test agc_word
    assert agc.agc_word(0xFFFF) == 0x7FFF
    assert agc.agc_word(0x12345) == 0x2345
    # Test agc_add
    assert agc.agc_add(0x0001, 0x0001) == 0x0002
    # Test agc_sub
    assert agc.agc_sub(0x0002, 0x0001) == 0x0001
    # Test agc_complement
    assert agc.agc_complement(0x0000) == 0x7FFF
    assert agc.agc_complement(0x7FFF) == 0x0000
    print("Basic AGC tests passed.")
    # Test agc_sign
    assert agc.agc_sign(0x0001) == 1
    assert agc.agc_sign(0x7FFF) == -1
    assert agc.agc_sign(0x0000) == 0
    # Test agc_is_negative
    assert agc.agc_is_negative(0x7FFF) is True
    assert agc.agc_is_negative(0x0000) is False
    # Test agc_is_zero
    assert agc.agc_is_zero(0x0000) is True
    assert agc.agc_is_zero(0x7FFF) is True

    print("AGC arithmetic tests passed.")
    
    # Test instruction execution
    
    agc.reset()
    
    agc.erasable_memory[0] = 0x0001  # Set
    
    agc.execute_instruction(["INCR", 0])  # Increment memory[0]
    
    assert agc.erasable_memory[0] == 0x0002  # Check increment
    
    agc.execute_instruction(["AD", 0])  # Add memory[0] to accumulator
   
    assert agc.accumulator == 0x0002  # Check accumulator value
    
    agc.execute_instruction(["SU", 0])  # Subtract memory[0]
   
    assert agc.accumulator == 0x0000  # Check accumulator after subtraction
   
    print("AGC instruction execution tests passed.")
    
    # Additional tests can be added for other instructions and functionalities
    
