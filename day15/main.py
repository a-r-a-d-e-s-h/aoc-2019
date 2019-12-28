from collections import namedtuple


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
        self.instruction_pointer += size  # gets changed later in jumps
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


class Vec(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, vec):
        return Vec(*map(sum, zip(self, vec)))

    def __sub__(self, vec):
        return Vec(*map(lambda x, y: x - y, self, vec))

    def __neg__(self):
        return Vec(*map(lambda x: -x, self))


class Movement:
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    VECTORS = {
        NORTH: Vec(0, -1),
        SOUTH: Vec(0, 1),
        WEST: Vec(-1, 0),
        EAST: Vec(1, 0)
    }

    DIRECTIONS = [NORTH, SOUTH, EAST, WEST]

    @classmethod
    def as_vector(cls, val):
        return cls.VECTORS[val]


class ResponseCode:
    HIT_WALL = 0
    MOVED = 1
    OXYGEN = 2


class Tile:
    WALL = '#'
    PATH = '.'
    OXYGEN = 'o'
    UNKNOWN = ' '


class Droid:
    display = None

    def __init__(self, comp, start_pos=(0, 0)):
        self.comp = comp
        self.pos = Vec(*start_pos)
        self.map = {self.pos: Tile.PATH}
        self.path_in_progress = []

    def plot_map(self):
        self.comp.load()
        def direction_getter(comp):
            if self.path_in_progress:
                comp.direction = self.path_in_progress.pop()
                return comp.direction
            node = self.to_investigate()
            if node is None:
                return 0
            while node.parent is not None:
                self.path_in_progress.append(node.direction)
                node = node.parent
            return direction_getter(comp)

        comp = self.comp
        comp.input_getter = direction_getter

        counter = 0
        while 1:
            counter += 1
            comp.run()
            if comp.halted:
                break
            output = comp.output_val
            new_pos = self.pos + Movement.as_vector(comp.direction)
            if output in (1, 2):
                self.pos = new_pos
                if output == 1:
                    self.map[new_pos] = Tile.PATH
                elif output == 2:
                    self.map[new_pos] = Tile.OXYGEN
            else:
                self.map[new_pos] = Tile.WALL

    def to_investigate(self):
        # Find the nearest unexplored square.
        Node = namedtuple("Node", ("pos", "parent", "direction"))
        to_do = [Node(self.pos, None, None)]
        visited = []
        while to_do:
            new_to_do = []
            for node in to_do:
                visited.append(node.pos)
                tile = self.map[node.pos]
                for direction in range(1, 5):
                    test_vec = node.pos + Movement.as_vector(direction)
                    test_tile = self.get_tile(*test_vec)
                    test_node = Node(test_vec, node, direction)
                    if test_tile in [Tile.PATH, Tile.OXYGEN]:
                        if test_vec not in visited:
                            new_to_do.append(test_node)
                    elif test_tile == Tile.UNKNOWN:
                        return test_node
            to_do = new_to_do
        return None

    def distances_to(self, vectors):
        """Choose a direction which minimises our distance to a vector"""
        walkable = []
        knowns = {vec: 0 for vec in vectors}
        to_do = list(vectors)
        for pos, tile in self.map.items():
            if tile in (Tile.PATH, Tile.OXYGEN):
                walkable.append(pos)

        while to_do:
            new_to_do = []
            while to_do:
                pos = to_do.pop()
                for direction in Movement.VECTORS.values():
                    test_pos = pos + direction
                    if test_pos in walkable:
                        if test_pos not in knowns:
                            knowns[test_pos] = knowns[pos] + 1
                            new_to_do.append(test_pos)
            to_do = new_to_do

        return knowns

    def direction_to(self, vectors):
        knowns = self.distances_to(vectors)

        pos = self.pos
        val = knowns[pos]
        for direction, vec in Movement.VECTORS.items():
            new_pos = pos + vec
            if new_pos not in knowns:
                continue
            if knowns[new_pos] < val:
                return direction

    def distances_to_oxygens(self):
        return self.distances_to(self.get_oxygens())

    def get_oxygens(self):
        oxygens = []
        for vec, tile in self.map.items():
            if tile == Tile.OXYGEN:
                oxygens.append(vec)
        return oxygens

    def display_map(self, with_droid=False):
        coords = self.map.keys()
        min_x = min(c[0] for c in coords)
        max_x = max(c[0] for c in coords)
        min_y = min(c[1] for c in coords)
        max_y = max(c[1] for c in coords)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        layout = []
        for y in range(height):
            line = []
            for x in range(width):
                line.append(self.get_tile(x + min_x, y + min_y))
            layout.append(line)
        if with_droid:
            x, y = self.pos
            layout[y - min_y][x - min_x] = 'D'
        for row in layout:
            print(''.join(row))

    def get_tile(self, x, y):
        if Vec(x, y) in self.map:
            return self.map[Vec(x, y)]
        else:
            return Tile.UNKNOWN


def solve_1(droid):
    return droid.distances_to_oxygens()[Vec(0, 0)]


def solve_2(droid):
    distances = droid.distances_to_oxygens()
    return distances[max(distances, key=lambda x: distances[x])]


def main():
    comp = Computer('input.txt')
    droid = Droid(comp)
    droid.plot_map()
    print(solve_1(droid))
    print(solve_2(droid))


if __name__ == "__main__":
    main()
