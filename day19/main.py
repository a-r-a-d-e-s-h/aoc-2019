from bisect import bisect_left
from itertools import count
import math
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
        self.instruction_pointer += size  # gets changed later in jump
        for index in range(len(params)):
            mode = modes[index]
            if modes[index] == 2:
                params[index] += self.relative_base

        dparams = []  # parameters dereferenced according to mode
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


class BisectRange:
    def __init__(self, func, lower, upper):
        self.func = func
        self.lower = lower
        self.upper = upper

    def __len__(self):
        return self.upper - self.lower + 1

    def __getitem__(self, v):
        return self.func(v + self.lower)

    def bisect(self, val):
        return self.lower + bisect_left(self, val)


class TractorBeam:
    """
    For accessing the tractor beam computer, and predicting its behaviour

    We run the intcode program to get specific data, but we run on an
    assumption that there are constants 0 < a < b such that a coordinate (x, y)
    lies within the tractor beam if and only if ay <= x <= by, and use this
    assumption to take shortcuts where possible.
    """

    def __init__(self, filename):
        self.comp = Computer(filename)
        self.a = None
        self.b = None
        self.known_bounds = {0: (0, 0)}
        self.highest_known_bounds = 0
        self.calls = 0

    def __str__(self):
        if self.a is not None:
            return "<TractorBeam: [{}<a<={}, {}<=b<{}]>".format(
                    *self.a, *self.b)
        else:
            return "<TractorBeam: Bounds unknown>"

    def check_pos(self, x, y):
        self.calls += 1
        self.comp.load()
        self.comp.run([x, y])
        return self.comp.output_val

    def get_for_pos(self, x, y):
        pass

    def get_bounds_for_row(self, row):
        if row in self.known_bounds:
            return self.known_bounds[row]
        else:
            return self.calculate_bounds_for_row(row)

    def calculate_bounds_for_row(self, row):
        if self.a is None:
            self.initialise_bounds()
        if row > self.highest_known_bounds*2:
            # Don't jump more than twice what we already know.
            # If so, do some smaller ones first.
            self.calculate_bounds_for_row(row//2 + 1)

        # Now we actually calculate what we have.
        # lower bound...
        min_x = math.floor(self.a[0]*row) + 1
        max_x = math.ceil(self.a[1]*row) - 1
        lower_x = self.find_lower_bound(row, min_x, max_x)
        # upper bound...

        min_x = math.floor(self.b[0]*row) + 1
        max_x = math.ceil(self.b[1]*row) - 1
        upper_x = self.find_upper_bound(row, min_x, max_x)
        self.known_bounds[row] = (min_x, max_x)
        self.highest_known_bounds = max(row, self.highest_known_bounds)
        if lower_x <= upper_x:
            self.update_bounds(row, lower_x, upper_x)
        return (lower_x, upper_x)

    def find_lower_bound(self, row, lower, upper):
        def func(v):
            return self.check_pos(v, row)
        bisector = BisectRange(func, lower, upper)
        return bisector.bisect(1)  # Where is first 1

    def find_upper_bound(self, row, lower, upper):
        def func(v):
            return -self.check_pos(v, row)
        bisector = BisectRange(func, lower, upper)
        return bisector.bisect(0) - 1  # Where is last 1

    def initialise_bounds(self):
        y, (x_l, x_r) = self.find_nontrivial_row()
        self.a = [(x_l-1)/y, x_l/y]
        self.b = [x_r/y, (x_r+1)/y]
        self.highest_known_bounds = y

    def update_bounds(self, y, x_l, x_r):
        self.a[0] = max(self.a[0], (x_l - 1)/y)
        self.a[1] = min(self.a[1], x_l/y)
        self.b[0] = max(self.b[0], x_r/y)
        self.b[1] = min(self.b[1], (x_r + 1)/y)

    def find_nontrivial_row(self):
        """Search for the first row with 1's in, other than x=y=0"""
        for i in count(1):
            for y in range(i + 1):  # Do a diagonal sweep.
                x = i - y
                if self.check_pos(x, y):
                    break
            else:
                continue
            break
        # The (x, y) will be a nontrivial point in the tractor beam.
        # We will now find the start and finish of this row.
        return y, self.seek_bounds_for_row(y, x, x)

    def seek_bounds_for_row(self, row, x_left, x_right):
        """
        Find start and end bounds for the row, with starting vals.

        Assume that (x_left, row) and (x_right, row) are in the tractor beam,
        and that x_left <= x_right. We walk left from (x_left, row) until we
        find squares outside the tractor beam, and right from (x_right, row).
        """
        left_bound = x_left
        while 1:
            if self.check_pos(left_bound - 1, row):
                left_bound -= 1
            else:
                break

        right_bound = x_right
        while 1:
            if self.check_pos(right_bound + 1, row):
                right_bound += 1
            else:
                break
        bounds = (left_bound, right_bound)
        self.known_bounds[row] = bounds
        return bounds


def solve_1(tractor_beam, dimension):
    tot = 0
    for y in range(50):
        if tractor_beam.a is not None:
            if math.floor(y * tractor_beam.a[0]) + 1 >= 50:
                break
        u, v = tractor_beam.get_bounds_for_row(y)
        v = min(v, 49)
        if u <= v:
            tot += v + 1 - u
    return tot


def solve_2(tractor_beam, dimension):
    boundaries = {}
    counter = 100
    for counter in count(100):
        top = tractor_beam.get_bounds_for_row(counter - dimension + 1)
        bot = tractor_beam.get_bounds_for_row(counter)
        if top[1] - bot[0] >= dimension - 1:
            break
    return 10000*bot[0] + counter - dimension + 1


def main():
    import time
    start = time.time()
    comp = Computer(filename)
    tractor_beam = TractorBeam(filename)
    print(solve_1(tractor_beam, 50))
    print(solve_2(tractor_beam, 100))
    print("elapsed: {:.2f}s".format(time.time() - start))


main()
