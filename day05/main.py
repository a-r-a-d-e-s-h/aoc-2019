input_file = "input.txt"

class Computer:
    OPERATIONS = {
        1: 'add',
        2: 'mul',
        3: 'use_input',
        4: 'ret_output',
        5: 'jump_if_true',
        6: 'jump_if_false',
        7: 'less_than',
        8: 'equals',
        99: 'end'
    }
    def __init__(self, program):
        self.program = tuple(program)
        self.memory = list(program)
        self.instruction_pointer = 0
        self.parameter_mode = 0
        self.input_val = None

    def load(self):
        self.memory = list(self.program)
        self.instruction_pointer = 0
        self.parameter_mode = 0

    def run(self, input_val=None):
        self.input_val = input_val
        while 1:
            if self.step():
                break
        return self.input_val

    def step(self):
        ip = self.instruction_pointer
        opcode = self.memory[ip]
        opcode, modes = self.parse_opcode(opcode)
        func = self.get_func_for_opcode(opcode)
        return func(modes)

    def parse_opcode(self, opcode):
        normal_opcode = opcode % 100
        modes = "{:03d}".format(opcode // 100)
        modes = tuple(map(int, modes[::-1]))
        return (normal_opcode, modes)

    def get_func_for_opcode(self, opcode):
        return getattr(self, self.OPERATIONS[opcode])

    def add(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 4]
        if modes[0] == 0:
            x0 = self.memory[params[0]]
        else:
            x0 = params[0]

        if modes[1] == 0:
            x1 = self.memory[params[1]]
        else:
            x1 = params[1]
        self.memory[params[2]] = x0 + x1
        self.instruction_pointer += 4

    def mul(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 4]
        if modes[0] == 0:
            x0 = self.memory[params[0]]
        else:
            x0 = params[0]

        if modes[1] == 0:
            x1 = self.memory[params[1]]
        else:
            x1 = params[1]
        self.memory[params[2]] = x0 * x1
        self.instruction_pointer += 4

    def use_input(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 2]
        self.memory[params[0]] = self.input_val
        self.instruction_pointer += 2

    def ret_output(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 2]
        self.input_val = self.memory[params[0]]
        self.instruction_pointer += 2

    def jump_if_true(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 3]
        if modes[0] == 0:
            test_val = self.memory[params[0]]
        else:
            test_val = params[0]
        if modes[1] == 0:
            addr = self.memory[params[1]]
        else:
            addr = params[1]
        if test_val:
            self.instruction_pointer = addr
        else:
            self.instruction_pointer += 3

    def jump_if_false(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 3]
        if modes[0] == 0:
            test_val = self.memory[params[0]]
        else:
            test_val = params[0]
        if modes[1] == 0:
            addr = self.memory[params[1]]
        else:
            addr = params[1]
        if test_val == 0:
            self.instruction_pointer = addr
        else:
            self.instruction_pointer += 3

    def less_than(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 4]
        if modes[0] == 0:
            x0 = self.memory[params[0]]
        else:
            x0 = params[0]

        if modes[1] == 0:
            x1 = self.memory[params[1]]
        else:
            x1 = params[1]
        self.memory[params[2]] = int(x0 < x1)
        self.instruction_pointer += 4

    def equals(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 4]
        if modes[0] == 0:
            x0 = self.memory[params[0]]
        else:
            x0 = params[0]

        if modes[1] == 0:
            x1 = self.memory[params[1]]
        else:
            x1 = params[1]
        self.memory[params[2]] = int(x0 == x1)
        self.instruction_pointer += 4

    def end(self, model):
        self.instruction_pointer += 1
        return 1




def main():
    text = open(input_file).read()
    data = list(map(int, text.split(',')))
    computer = Computer(data)
    computer.load()
    print(computer.run(1))
    computer.load()
    print(computer.run(5))


main()
