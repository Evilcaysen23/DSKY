
class Computer:
    def __init__(self, name, computer_type):
        self.name = name

        self.computer_type = computer_type

        if computer_type == 'AGC':
            self.ReadonlyMemory = 36864
            self.WriteableMemory = 2048
            print("AGC Computer Type")
        else:
            self.ReadonlyMemory = 0
            self.WriteableMemory = 0
            print("Unknown Computer Type")
        if name == "CSM":
            self.program = "Comanche"
            print("Comanche")
        elif name == "LM":
            self.program = "Luminary"
            print("Luminary")
        else:
            self.program = "Unknown"
            print("Unknown program for this computer type")
#make computer type = AGC and Name of computer = CSM
csm_computer = Computer('CSM', 'AGC')
