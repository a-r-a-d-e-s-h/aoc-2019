from collections import defaultdict, deque


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
    input_needed = False
    block_on_input = False

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
        self.needs_input = False
        while not (self.halted or self.paused):
            if self.step():
                break
        return self.output_val

    def step(self):
        ip = self.instruction_pointer
        opcode = self.memory[ip]
        opcode, modes = self.parse_opcode(opcode)
        sigs = self.OP_SIGNATURES[self.OPERATIONS[opcode]]
        if self.need_input(opcode) and self.block_on_input:
            self.input_needed = True
            return 1
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

    def need_input(self, opcode):
        if self.OPERATIONS[opcode] in ["use_input"]:
            return not self.input_vals


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


def solve_1(fn):
    comps = []
    for addr in range(50):
        comp = Computer(fn)
        comp.load()
        comp.packets = deque()
        comp.input_return_vals = deque()
        comp.block_on_input = True
        comp.input_vals = [addr]
        comps.append(comp)

    queue = defaultdict(list)
    all_halted = False
    while not all_halted:
        all_halted = True
        for comp_addr, comp in enumerate(comps):
            if not comp.halted:
                all_halted = False
                comp.run()
            else:
                continue
            if comp.paused:
                # We have output. expect two more
                address = comp.output_val
                packet = []
                for i in range(2):
                    comp.run()
                    packet.append(comp.output_val)
                queue[address].append(packet)
                if address == 255:
                    return packet[1]
            elif comp.input_needed:
                try:
                    packet = queue[comp_addr].pop(0)
                except IndexError:
                    comp.input_vals.append(-1)
                else:
                    comp.input_vals.extend(packet)


def solve_2(fn):
    comps = []
    for addr in range(50):
        comp = Computer(fn)
        comp.load()
        comp.packets = deque()
        comp.input_return_vals = deque()
        comp.block_on_input = True
        comp.input_vals = [addr]
        comps.append(comp)

    queue = defaultdict(list)
    all_halted = False
    idle_limit = 10
    nat_val = None
    idle_counter = 0
    last_y = None
    while not all_halted:
        all_halted = True
        have_output = False
        for comp_addr, comp in enumerate(comps):
            if not comp.halted:
                all_halted = False
                comp.run()
            else:
                continue
            if comp.paused:
                # We have output. expect two more
                address = comp.output_val
                have_output = True
                packet = []
                for i in range(2):
                    comp.run()
                    packet.append(comp.output_val)
                queue[address].append(packet)
                if address == 255:
                    nat_val = packet
            elif comp.input_needed:
                try:
                    packet = queue[comp_addr].pop(0)
                except IndexError:
                    comp.input_vals.append(-1)
                else:
                    comp.input_vals.extend(packet)
        if have_output:
            idle_counter = 0
        else:
            idle_counter += 1
        if idle_counter >= idle_limit:
            queue[0].append(nat_val)
            if nat_val[1] == last_y:
                return last_y
            else:
                last_y = nat_val[1]
            idle_counter = 0




def main():
    filename = "input.txt"
    print(solve_1(filename))
    print(solve_2(filename))


if __name__ == "__main__":
    main()
