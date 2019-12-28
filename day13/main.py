import time

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

    def __init__(self, program):
        self.program = tuple(program)
        self.memory = list(program)
        self.instruction_pointer = 0
        self.relative_base = 0
        self.input_vals = []
        self.halted = True
        self.paused = True
        self.input_getter = None

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
            return self.input_getter()
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


class Tile:
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4

    SYMBOLS = {
        EMPTY: ' ',
        WALL: '#',
        BLOCK: '^',
        PADDLE: '=',
        BALL: 'o'
    }

    @classmethod
    def display(cls, val):
        return cls.SYMBOLS[val]


def load_squares(data):
    comp = Computer(data)
    comp.load()
    vals = []
    while 1:
        comp.run()
        if comp.halted:
            break
        vals.append(comp.output_val)
    squares = []
    for i in range(len(vals)//3):
        items = vals[i*3:(i+1)*3]
        squares.append(items)
    return squares
    

def solve_1(data):
    squares = load_squares(data)
    tot = 0
    for sq in squares:
        if sq[2] == Tile.BLOCK:
            tot += 1
    return tot


def build_display_and_get_score(comp):
    positions = {}
    stop = False

    while 1:
        item = []
        score = None
        for i in range(3):
            comp.run()
            if comp.halted:
                stop = True
                print("Breaking with i={}".format(i))
                break
            item.append(comp.output_val)
        if stop:
            break
        x, y, val = item
        if (x, y) == (-1, 0):
            score = val
            break
        positions[x, y] = val


    max_x = max(coord[0] for coord in positions.keys())
    max_y = max(coord[1] for coord in positions.keys())
    width = max_x + 1
    height = max_y + 1
    display = [[0]*width for __ in range(height)]
    for (x, y), val in positions.items():
        display[y][x] = val
    return display, score


def play_game(comp, game):
    while 1:
        item = []
        for i in range(3):
            comp.run()
            if comp.halted:
                print(game.score)
                return
            item.append(comp.output_val)
        x, y, val = item
        if (x, y) == (-1, 0):
            game.score = val
        else:
            game.update(item)


class GameState:
    def __init__(self, display, score):
        self.score = score
        self.display = display

    def update(self, item):
        x, y, val = item
        self.display[y][x] = val

    def print_display(self):
        for row in self.display:
            print(''.join(map(Tile.display, row)))
        print("Score: {}".format(self.score))

    def find_paddle(self):
        for y, row in enumerate(self.display):
            for x, val in enumerate(row):
                if val == Tile.PADDLE:
                    return (x, y)

    def find_ball(self):
        for y, row in enumerate(self.display):
            for x, val in enumerate(row):
                if val == Tile.BALL:
                    return (x, y)




def solve_2(data):
    data[0] = 2
    comp = Computer(data)
    comp.load()

    display, score = build_display_and_get_score(comp)
    game = GameState(display, score)

    def ai_player():
        paddle = game.find_paddle()
        ball = game.find_ball()

        if ball[0] < paddle[0]:
            return -1
        elif ball[0] > paddle[0]:
            return 1
        else:
            return 0

    comp.input_getter = ai_player

    play_game(comp, game)
    
def main():
    data = list(map(int, open('input.txt').read().split(',')))
    print(solve_1(data))
    solve_2(data)

main()
