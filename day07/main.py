from itertools import cycle, permutations

filename = "input.txt"

class Computer:
    def __init__(self, program):
        self.program = tuple(program)
        self.memory = list(program)
        self.instruction_pointer = 0
        self.parameter_mode = 0
        self.input_vals = []
        self.halted = True

    def load(self):
        self.memory = list(self.program)
        self.instruction_pointer = 0
        self.parameter_mode = 0
        self.input_vals = []

    def run(self, input_vals=[]):
        self.input_vals.extend(input_vals)
        self.halted = False
        while 1:
            if self.step():
                break
        return self.output_val

    def step(self):
        ip = self.instruction_pointer
        opcode = self.memory[ip]
        opcode, modes = self.parse_opcode(opcode)
        func = self.get_func_for_opcode(opcode)
        return func(modes)

    def parse_opcode(self, opcode):
        normal_opcode = opcode % 100
        mode_1 = (opcode//100) % 10
        mode_2 = (opcode//1000) % 10
        mode_3 = (opcode//10000) % 10
        return (normal_opcode, (mode_1, mode_2, mode_3))

    def get_func_for_opcode(self, opcode):
        if opcode == 1:
            return self.add
        if opcode == 2:
            return self.mul
        if opcode == 3:
            return self.use_input
        if opcode == 4:
            return self.ret_output
        if opcode == 5:
            return self.jump_if_true
        if opcode == 6:
            return self.jump_if_false
        if opcode == 7:
            return self.less_than
        if opcode == 8:
            return self.equals
        if opcode == 99:
            return self.halt

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
        self.memory[params[0]] = self.get_input()
        self.instruction_pointer += 2

    def ret_output(self, modes):
        ip = self.instruction_pointer
        params = self.memory[ip + 1:ip + 2]
        self.output_val = self.memory[params[0]]
        self.instruction_pointer += 2
        return 1

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

    def halt(self, model):
        self.instruction_pointer += 1
        self.halted = True
        return 1

    def get_input(self):
        return self.input_vals.pop(0)


def solve_1(data):
    perms = permutations(range(5), 5)
    computers = [Computer(data) for __ in range(5)]
    outputs = []
    for perm in perms:
        next_input = 0
        for phase, comp in zip(perm, computers):
            comp.load()
            next_input = comp.run([phase, next_input])
        outputs.append(next_input)
    return max(outputs)

def solve_2(data):
    perms = permutations(range(5, 10), 5)
    computers = [Computer(data) for __ in range(5)]
    outputs = []
    for perm in perms:
        next_input = 0
        for phase, comp in zip(perm, computers):
            comp.load()
            comp.input_vals = [phase]
        for phase, comp in cycle(zip(perm, computers)):
            next_input = comp.run([next_input])
            if comp.halted:
                if perm.index(phase) == 4:
                    break
        outputs.append(next_input)
    return max(outputs)

def main():
    f = open(filename)
    data = list(map(int, f.read().split(',')))
    print(solve_1(data))
    print(solve_2(data))

main()
