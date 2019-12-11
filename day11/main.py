filename = "input.txt"

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
    PARAM_TYPES = (GET, SET)

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

    def __init__(self, program):
        self.program = tuple(program)
        self.memory = list(program)
        self.instruction_pointer = 0
        self.relative_base = 0
        self.parameter_mode = 0
        self.input_vals = []
        self.halted = True
        self.paused = True

    def load(self):
        self.memory = list(self.program)
        self.instruction_pointer = 0
        self.relative_base = 0
        self.parameter_mode = 0
        self.halted = True
        self.paused = True

    def get_addr(self, addr):
        if addr > len(self.memory) - 1:
            extra = addr - len(self.memory) + 1
            self.memory.extend([0] * extra)
        return self.memory[addr]

    def set_addr(self, addr, val):
        self.memory[addr] = val


    def run(self, input_vals=[]):
        if not isinstance(input_vals, (tuple, list)):
            input_vals = [input_vals]
        self.input_vals.extend(input_vals)
        self.halted = False
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
            param = params[index]
            mode = modes[index]
            if mode == 2:
                params[index] += self.relative_base

        dparams = [] # parameters dereferenced according to mode
        for param, mode in zip(params, modes):
            if mode in (0, 2):
                val = self.get_addr(param)
            elif mode == 1:
                val = param
            dparams.append(val)
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


class Panel:
    BLACK = 0
    WHITE = 1

class Position:
    def __init__(self, start, direction):
        self.pos = start
        self.dir = direction

    def rotate(self, direction):
        x, y = self.dir
        if direction == 0:
            self.dir = (y, -x)
        else:
            self.dir = (-y, x)

    def step(self):
        self.pos = tuple(map(sum, zip(self.pos, self.dir)))


def run_robot(data, start_tile=0):
    comp = Computer(data)
    from collections import defaultdict
    panels = defaultdict(int)
    panels[(0, 0)] = start_tile
    painted_panels = defaultdict(int)
    robot_pos = Position(
        start=(0, 0),
        direction=(0, -1)
    )

    comp.load()
    while 1:
        panel = panels[robot_pos.pos]
        comp.run(panel)
        if comp.halted:
            break
        colour = comp.output_val
        comp.run()
        direction = comp.output_val
        if comp.halted:
            break
        panels[robot_pos.pos] = colour
        painted_panels[robot_pos.pos] = colour
        robot_pos.rotate(direction)
        robot_pos.step()
    return painted_panels


def solve_1(data):
    output = run_robot(data, start_tile=0)
    return len(output)

def solve_2(data):
    output = run_robot(data, start_tile=1)
    positions = output.keys()

    min_x = min(pos[0] for pos in positions)
    max_x = max(pos[0] for pos in positions)
    min_y = min(pos[1] for pos in positions)
    max_y = max(pos[1] for pos in positions)

    lines = []
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            row.append(output[x, y])
        row = ['#' if item else ' ' for item in row]
        lines.append(''.join(row))
    return '\n'.join(lines)


def main():
    text = open(filename).read()
    data = list(map(int, text.split(',')))
    print(solve_1(data))
    print(solve_2(data))

main()
