class Computer:
    def __init__(self, name, computer_type):
        # ... setup code ...
        self.verbs = {}
        self.programs = {}
        self.setup_programs_and_verbs()

    def setup_programs_and_verbs(self):
        self.programs[0] = self.program_Idler
        self.programs[1] = self.program_boot
        self.programs[2] = self.program_hello
        self.verbs[37] = self.run_program
        self.verbs[6] = self.display_data

    def execute_verb_noun(self, verb, noun):
        verb_func = self.verbs.get(verb)
        if verb_func:
            verb_func(noun)
        else:
            print("Invalid VERB")

    def run_program(self, noun):
        program = self.programs.get(noun)
        if program:
            program()
        else:
            print(f"Program {noun} not found.")

    def display_data(self, noun):
        print(f"Displaying data for noun {noun}")

    def program_Idler(self):
        print("Idler program running...")
        # Simulate idling behavior
    def program_boot(self):
        r1 = 0
        r2 = 0
        r3 = 0
        print("Booting AGC...")
        print(f"Registers: R1={r1}, R2={r2}, R3={r3}")
        self.execute_verb_noun(37, 0)  # Runs boot program

    def program_hello(self):
        print("Hello from AGC!")
    

# Usage
agc = Computer("CSM", "AGC")
agc.execute_verb_noun(37, 1)  # Runs boot program
