from collections import defaultdict
import copy
import operator
import re

filename = "input.txt"

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

class Vec(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, vec):
        return Vec(*map(sum, zip(self, vec)))

    def __sub__(self, vec):
        return Vec(*map(lambda x, y: x - y, self, vec))

    def __neg__(self):
        return Vec(*map(lambda x: -x, self))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]


def get_array(comp):
    comp.load()
    output = []
    while 1:
        comp.run()
        if comp.halted:
            break
        if comp.paused:
            output.append(chr(comp.output_val))
    text = ''.join(output)
    output = [list(row) for row in text.split('\n') if row]
    return output


class Tile:
    SCAFFOLD = '#'
    EMPTY = '.'


class Robot:
    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)
        self.parse_grid()
        self.direction = Vec(0, -1)

    def parse_grid(self):
        grid = self.grid
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile == '^':
                    self.grid[y][x] = Tile.SCAFFOLD
                    self.pos = Vec(x, y)
                    return

    def display_grid(self):
        grid = self.grid
        for row in grid:
            print(''.join(row))

DIRECTIONS = [Vec(0, -1), Vec(0, 1), Vec(1, 0), Vec(-1, 0)]


def solve_1(grid):
    height = len(grid)
    width = len(grid[0])
    intersections = []
    for y in range(1, height-1):
        for x in range(1, width-1):
            if grid[y][x] != Tile.SCAFFOLD:
                continue
            vec = Vec(x, y)
            scaffolds = 0
            for mov in DIRECTIONS:
                test = vec + mov
                if grid[test[1]][test[0]] != Tile.SCAFFOLD:
                    break
            else:
                intersections.append(vec)
    res = 0
    for item in intersections:
        res += item[0] * item[1]
    return res


class FallenOffScaffoldException(Exception):
    pass


class Puz2:
    DIRECTIONS = {
        '^': Vec(0, -1),
        '>': Vec(1, 0),
        '<': Vec(-1, 0),
        'v': Vec(0, 1)
    }
    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)
        self.DIRECTION_VECTORS = {
            self.DIRECTIONS[glyph]: glyph for glyph in self.DIRECTIONS
        }
        self.init_grid()

    def init_grid(self):
        for vec, tile in self.iterate():
            if tile in self.DIRECTIONS:
                self.pos = vec
                self.dir = self.DIRECTIONS[tile]
                self.grid[vec.y][vec.x] = '.'

    def iterate(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                yield Vec(x, y), tile

    def rotate(self, command):
        x, y = self.dir
        if command == 'L':
            self.dir = Vec(y, -x)
        elif command == 'R':
            self.dir = Vec(-y, x)

    def forwards(self, n):
        new_pos = self.pos
        for i in range(n):
            new_pos = new_pos + self.dir
            if self.grid[new_pos.y][new_pos.x] != '#':
                raise FallenOffScaffoldException()
        self.pos = new_pos

    def naive_walk(self):
        visited = {self.pos}
        commands = []
        def forwards():
            self.forwards(1)
            visited.add(self.pos)
            if commands and isinstance(commands[-1], int):
                commands[-1] += 1
            else:
                commands.append(1)

        def left():
            self.rotate('L')
            commands.append('L')

        def right():
            self.rotate('R')
            commands.append('R')

        def is_on_board(vec):
            try:
                self.grid[vec.y][vec.x]
            except IndexError:
                return False
            else:
                return True

        def tile_ahead():
            test_pos = self.pos + self.dir
            if is_on_board(test_pos):
                return self.grid[test_pos.y][test_pos.x]
            else:
                return None

        def unvisited_neighbours():
            for direction in self.DIRECTION_VECTORS:
                pos = direction + self.pos
                if (is_on_board(pos)
                        and self.grid[pos.y][pos.x] == '#'
                        and pos not in visited):
                    return True
            return False


        while 1:
            # Can we go forwards?
            tile = tile_ahead()
            if tile == '#':
                forwards()
            else:
                # Do we have any unvisited neighbouring squares to go to?
                if unvisited_neighbours():
                    # Does turning left help?
                    self.rotate('L')
                    tile = tile_ahead()
                    self.rotate('R')  # undo rotation
                    if tile is None:
                        continue  # Not on the board!

                    if tile == '#':
                        left()
                    else:  # left was no good. go right instead
                        right()
                else:
                    break

        # has this naive walk covered the whole scaffold?
        # Raise an exception if not...

        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == '#' and Vec(x, y) not in visited:
                    raise RuntimeError("Invalid scaffold for this method")

        return commands

    def __str__(self):
        self.grid[self.pos.y][self.pos.x] = self.DIRECTION_VECTORS[self.dir]
        text = '\n'.join(''.join(row) for row in self.grid)
        self.grid[self.pos.y][self.pos.x] = '.'
        return text


def plot_a_route(grid):
    puz = Puz2(grid)
    commands = puz.naive_walk()
    return commands
    

class CommandSegment:
    def __init__(self, commands):
        self.base_commands = commands

    def find_patterns(self):
        alg, pats = self.find_patterns_recursive([self.base_commands])
        pats = (','.join(map(str, pat)) for pat in pats)
        return alg, tuple(pats)

    def split_by_sublist(self, x, s):
        len_x = len(x)
        len_s = len(s)
        done_up_to = 0
        offset = 0
        ret = []
        while offset <= len_x - 1:
            if x[offset:offset + len_s] == s:
                if offset > done_up_to:
                    ret.append(x[done_up_to:offset])
                offset = offset + len_s
                done_up_to = offset
                continue
            offset += 1
        else:
            if done_up_to < len_x:
                ret.append(x[done_up_to:])
        return ret

    def find_patterns_recursive(self, command_lists, given_patterns=()):
        if len(given_patterns) == 3:
            if not command_lists:
                alg = self.build_from_patterns(given_patterns)
                return alg, given_patterns
            remaining = sum(len(commands) for commands in command_lists)
            return
        patterns = defaultdict(list)
        for index, commands in enumerate(command_lists):
            for length in range(1, len(commands) + 1):
                for offset in range(0, len(commands) + 1 - length):
                    sub_commands = list(commands[offset:offset+length])
                    command_str = ','.join(map(str, sub_commands))
                    if len(command_str) <= 20:
                        if sub_commands not in patterns[length]:
                            patterns[length].append(sub_commands)

        for key in sorted(patterns.keys(), key=operator.neg):
            for pattern in patterns[key]:
                new_commands = []
                for commands in command_lists:
                    new_commands.extend(self.split_by_sublist(commands, pattern))
                res = self.find_patterns_recursive(
                    new_commands,
                    given_patterns + (pattern,)
                )
                if res is not None:
                    return res

    def build_from_patterns(self, patterns):
        str_command = ','.join(map(str, self.base_commands))
        for pattern, name in zip(patterns, ('A', 'B', 'C')):
            str_pattern = ','.join(map(str, pattern))
            remainder = re.split(str_pattern, str_command)
            str_command = name.join(remainder)
        return str_command

def solve_2(comp, grid):
    commands = plot_a_route(grid)
    seg = CommandSegment(commands)
    alg, pats = seg.find_patterns()

    comp.load()
    comp.memory[0] = 2
    lines = (alg,) + pats + ('n',)
    def input_iter():
        for line in lines:
            for char in line:
                yield ord(char)
            yield 10
    iterator = input_iter()
    def input_getter(comp):
        return next(iterator)

    comp.input_getter = input_getter
    while 1:
        comp.run()
        if comp.halted:
            print("Halted")
            return
        elif comp.paused:
            if comp.output_val >= 128:
                return comp.output_val
def main():
    comp = Computer(filename)
    grid = get_array(comp)
    robot = Robot(grid)
    print(solve_1(grid))
    print(solve_2(comp, grid))
    

main()
