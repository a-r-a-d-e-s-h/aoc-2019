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


class SpringDroid:
    NEW_LINE = 10
    TILE_REGISTERS = ('A', 'B', 'C', 'D')

    def __init__(self, comp):
        self.comp = comp

    def script_inputter(self, script):
        def gen():
            lines = script.splitlines()
            for line in lines:
                yield from (ord(c) for c in line)
                yield self.NEW_LINE
        gen = gen()
        def f(comp):
            return next(gen)
        return f

    def run_with_script(self, script):
        inputter = self.script_inputter(script)
        self.comp.load()
        self.comp.input_getter = inputter
        output_text = []
        while 1:
            self.comp.run()
            if self.comp.halted:
                break
            elif self.comp.paused:
                output = self.comp.output_val
                if output >= 128:
                    return (True, output)
                output_text.append(chr(output))
            else:
                raise Exception("Unhandled case?")
        return (False, output_text)

    def parse_output_data(self, data):
        lines = ''.join(data).splitlines()
        chunks = []
        last_chunk = []
        for line in lines:
            if not line and last_chunk:
                chunks.append(last_chunk)
                last_chunk = []
            elif line:
                last_chunk.append(line)
        return chunks[-5:]


def solve_1(comp):
    droid = SpringDroid(comp)
    script = [
        "OR A J",
        "AND B J",
        "AND C J",
        "NOT J J",
        "AND D J",
        "WALK"
    ]
    success, output = droid.run_with_script('\n'.join(script))
    if not success:
        print(''.join(output))
    else:
        return output


def solve_2(comp):
    droid = SpringDroid(comp)
    script = [
        "OR A J",
        "AND B J",
        "AND C J",
        "NOT J J",
        "AND D J",
        "OR H T",
        "OR E T",
        "AND T J",
        "RUN"
    ]
    success, output = droid.run_with_script('\n'.join(script))
    if not success:
        print(''.join(output))
    else:
        return output


def main():
    comp = Computer('input.txt')
    print(solve_1(comp))
    print(solve_2(comp))


if __name__ == "__main__":
    main()
