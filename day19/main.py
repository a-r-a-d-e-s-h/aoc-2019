filename = 'input.txt'


class HaltedError(Exception):
    pass

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
        9: 'offset_rel_base',
        99: 'halt'
    }

    GET = 'get'
    SET = 'set'

    OP_SIGNATURES = {
        'add': (GET, GET, SET),
        'mul': (GET, GET, SET),
        'less_than': (GET, GET, SET),
        'equals': (GET, GET, SET),
        'jump_if_true': (GET, GET),
        'jump_if_false': (GET, GET),
        'offset_rel_base': (GET,),
        'use_input': (SET,),
        'ret_output': (GET,),
        'halt': ()
    }
    instruction_pointer = 0
    relative_base = 0
    output_val = None
    input_getter = None
    halted = True
    paused = True

    def __init__(self, filename):
        self.program = self.load_from_filename(filename)
        self.memory = list(self.program)
        self.input_vals = []

    def load_from_filename(self, filename):
        with open(filename) as f:
            text = f.read()
            return tuple(map(int, text.split(',')))

    def load(self):
        self.memory = list(self.program)
        self.instruction_pointer = 0
        self.relative_base = 0
        self.parameter_mode = 0
        self.halted = False
        self.paused = True

    def get_addr(self, addr):
        if addr > len(self.memory) - 1:
            extra = addr - len(self.memory) + 1
            self.memory.extend([0] * extra)
        return self.memory[addr]

    def set_addr(self, addr, val):
        self.memory[addr] = val

    def run(self, input_vals=[]):
        if self.halted:
            raise HaltedError
        if not isinstance(input_vals, (tuple, list)):
            input_vals = [input_vals]
        self.input_vals.extend(input_vals)
        self.paused = False
        while not (self.halted or self.paused):
            if self.step():
                break
        return self.output_val

    def step(self):
        ip = self.instruction_pointer
        opcode = self.memory[ip]
        opcode, modes = self.parse_opcode(opcode)
        sigs = self.OP_SIGNATURES[self.OPERATIONS[opcode]]
        size = len(sigs) + 1
        params = self.memory[ip + 1:ip + size]
        self.instruction_pointer += size # gets changed later in jump functions
        for index in range(len(params)):
            mode = modes[index]
            if modes[index] == 2:
                params[index] += self.relative_base

        dparams = [] # parameters dereferenced according to mode
        for param, mode in zip(params, modes):
            if mode in (0, 2):
                param = self.get_addr(param)
            dparams.append(param)
        func = self.get_func_for_opcode(opcode)
        get_params = [p for p, sig in zip(dparams, sigs) if sig == self.GET]
        set_params = [p for p, sig in zip(params, sigs) if sig == self.SET]
        res = func(*get_params)
        if not isinstance(res, tuple):
            res = (res,)
        # If set_params is empty, this does nothing.
        for set_param, result in zip(set_params, res):
            self.set_addr(set_param, result)

    def parse_opcode(self, opcode):
        normal_opcode = opcode % 100
        modes = "{:03d}".format(opcode // 100)
        modes = tuple(map(int, modes[::-1]))
        return (normal_opcode, modes)

    def get_func_for_opcode(self, opcode):
        return getattr(self, self.OPERATIONS[opcode])

    def add(self, x, y):
        return x + y

    def mul(self, x, y):
        return x * y

    def less_than(self, x, y):
        return int(x < y)

    def equals(self, x, y):
        return int(x == y)

    def use_input(self):
        if not self.input_vals:
            return self.input_getter(self)
        return self.input_vals.pop(0)

    def ret_output(self, x):
        self.output_val = x
        self.paused = True

    def jump_if_true(self, x, y):
        if x:
            self.instruction_pointer = y

    def jump_if_false(self, x, y):
        return self.jump_if_true(not(x), y)

    def halt(self):
        self.halted = True

    def offset_rel_base(self, x):
        self.relative_base += x

def get_at_pos(comp, x, y):
    comp.load()

    def input_getter(comp):
        to_ret = input_getter.vals.pop(0)
        return to_ret
    comp.input_getter = input_getter
    input_getter.vals = [x, y]
    comp.run()
    return comp.output_val

def solve_1(comp, dimension, do_print=False):
    tot = 0
    for y in range(dimension):
        for x in range(dimension):
            output = get_at_pos(comp, x, y)
            tot += bool(output)
            if do_print:
                print(output, end='')
        if do_print:
            print()
    return tot

def find_boundaries_brute_force(comp, n):
    x = 0
    while 1:
        res = get_at_pos(comp, x, n)
        if res:
            break
        x += 1
    start = x
    while 1:
        res = get_at_pos(comp, x, n)
        if res == 0:
            break
        x+= 1
    end = x - 1
    return (start, end)

def find_boundaries(comp, n, first_guess):
    x = first_guess[0]
    while 1:
        res = get_at_pos(comp, x, n)
        if res:
            break
        x += 1
    start = x
    x = first_guess[1]
    while 1:
        res = get_at_pos(comp, x, n)
        if res == 0:
            break
        x += 1
    end = x - 1
    return (start, end)

def solve_2(comp, dimension):
    test_val = 10
    next_guess = find_boundaries_brute_force(comp, test_val)
    boundaries = {}
    counter = test_val
    while 1:
        next_guess = find_boundaries(comp, counter, next_guess)
        boundaries[counter] = next_guess

        if counter - test_val + 1 >= dimension:
            top = boundaries[counter - dimension + 1]
            bot = boundaries[counter]
            if top[1] - bot[0] >= dimension - 1:
                break
        counter += 1
    return 10000*bot[0] + counter - dimension + 1


def main():
    comp = Computer(filename)
    print(solve_1(comp, 50))
    print(solve_2(comp, 100))

main()
