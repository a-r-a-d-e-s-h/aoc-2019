from bisect import bisect_left
from collections import defaultdict, deque, namedtuple

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

class Puz:
    DIRECTIONS = [Vec(0, 1), Vec(0, -1), Vec(1, 0), Vec(-1, 0)]
    State = namedtuple("State", ('keys', 'droids'))

    def __init__(self, grid):
        self.grid = grid
        self.init_grid()
        self.init_keys()
        self.init_tables()

    def init_keys(self):
        self.total_keys = 0
        self.all_keys = []
        for vec, tile in self.iterate():
            if tile.islower():
                self.total_keys += 1
                self.all_keys.append(tile)

    def init_grid(self):
        self.droid_positions = []
        for vec, tile in self.iterate():
            if tile == '@':
                self.droid_positions.append(vec)

    def init_tables(self):
        self.tables = []
        for pos in self.droid_positions:
            self.tables.append(self.tables_from_pos(pos)) 

    def tables_from_pos(self, pos):
        tables = {}
        to_do = [pos]
        tile_at_pos = self.grid[pos.y][pos.x]
        if tile_at_pos in ('.', '#'):
            raise RuntimeError("Invalid start point.")
        done = []
        while to_do:
            next_to_do = []
            for pos in to_do:
                tile = self.grid[pos.y][pos.x]
                tables[tile] = self.keys_from_pos(pos)
                done.append(tile)
                for destination, entry in tables[tile].items():
                    if destination not in done:
                        next_to_do.append(entry.pos)
            to_do = next_to_do
        return tables


    def keys_from_pos(self, pos, locked=()):
        Node = namedtuple('Node', ('pos', 'parent', 'dist'))
        to_do = [Node(pos, 0, None)]
        visited = deque([pos])
        dist = 0
        def have_visited(vec):
            tot_visited = len(visited)
            index = bisect_left(visited, vec)
            if index >= tot_visited:
                return (False, index)
            else:
                if visited[index] != vec:
                    return (False, index)
                else:
                    return (True, index)

        keys_reached = {}
        while to_do:
            next_to_do = []
            dist += 1
            for node in to_do:
                tile = self.grid[node.pos.y][node.pos.x]
                if tile.islower() and node.pos != pos:
                    keys_reached[tile] = node
                    continue

                for direction in self.DIRECTIONS:
                    test_vec = node.pos + direction
                    test_tile = self.grid[test_vec.y][test_vec.x]
                    if test_tile != '#' and test_tile not in locked:
                        is_visited, index = have_visited(test_vec)
                        if not is_visited:
                            next_to_do.append(Node(test_vec, node, dist))
                            visited.insert(index, test_vec)
            to_do = next_to_do
        
        # We want to return the distances from this position for each key, plus
        # any doors along the way.
        table = {}
        Entry = namedtuple("Entry", ('pos', 'distance', 'doors'))
        for key_name in keys_reached:
            node = keys_reached[key_name]
            key_pos = node.pos
            path = []
            while node.parent:
                path.append(node)
                node = node.parent
            path_doors = []
            for node in path:
                tile = self.grid[node.pos.y][node.pos.x]
                if tile.isupper():
                    path_doors.append(tile)
            table[key_name] = Entry(key_pos, len(path), path_doors[::-1])
        return table

    def get_initial_state(self):
        return self.State((), ('@',)*len(self.droid_positions))

    def min_path(self):
        # Each state of an explored solution will be represented by a
        # collection of values. This will be a tuple of two tuples. The first
        # being the list of all keys currently held, in alphabetal order. The
        # second being the current location of each droid, represented by the
        # character value of its tile. i.e. @ for start, or key name otherwise.
        # We don't store intermediate positions, we hop directly to the next
        # key. For each number of steps taken, we will have a deque of all
        # states to explore from that point.
        State = self.State
        initial = self.get_initial_state()
        distances = defaultdict(list, {0: [initial]})
        visited_states = deque([initial])
        visited_distances = deque([0])
        counter = 0

        def find_state(state):
            index = bisect_left(visited_states, state)
            total = len(visited_states)
            if index >= total:
                return (False, index)
            if visited_states[index] != state:
                return (False, index)
            else:
                return (True, index)

        max_keys_found = 0
        while 1:
            for state in distances[counter]:
                if len(state.keys) >= self.total_keys:
                    return counter
                if len(state.keys) > max_keys_found:
                    max_keys_found = len(state.keys)
                max_keys_found = max(max_keys_found, len(state.keys))
                for index, start in enumerate(state.droids):
                    table = self.tables[index][start]
                    for end, entry in table.items():
                        if not all(d.lower() in state.keys for d in entry.doors):
                            # We cannot get to this key, locked doors in way.
                            continue
                        new_dist = counter + entry.distance
                        if end in state.keys:
                            new_keys = state.keys
                        else:
                            new_keys = tuple(sorted(state.keys + (end,)))
                        new_droids = list(state.droids)
                        new_droids[index] = end
                        new_droids = tuple(new_droids)
                        new_state = State(new_keys, new_droids)
                        have_state, new_index = find_state(new_state)
                        if not have_state:
                            distances[new_dist].append(new_state)
                            visited_states.insert(new_index, new_state)
                            visited_distances.insert(new_index, new_dist)
                        else:
                            dist_for_state = visited_distances[new_index]
                            if dist_for_state > new_dist:
                                distances[dist_for_state].remove(new_state)
                                distances[new_dist].append(new_state)
                                visited_distances[new_index] = new_dist
            del distances[counter]
            counter += 1

    def iterate(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                yield Vec(x, y), tile

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.grid)


def solve_1(grid):
    puz = Puz(grid)
    answer = puz.min_path()
    return answer


def solve_2(grid):
    puz = Puz(grid)
    start_vec = None
    for vec, tile in puz.iterate():
        if tile == '@':
            start_vec = vec
            break

    for dy in range(-1, 2):
        for dx in range(-1, 2):
            v = vec + (dx, dy)
            if dx and dy:
                grid[v.y][v.x] = '@'
            else:
                grid[v.y][v.x] = '#'

    # We will split the grid into four. Remove doors for keys that are not in
    # that sector, and solve each like normal, then add the results.
    sub_grids = [
        [row[:v.x] for row in grid[:v.y]],
        [row[v.x - 1:] for row in grid[:v.y]],
        [row[:v.x] for row in grid[v.y - 1:]],
        [row[v.x - 1:] for row in grid[v.y - 1:]]
    ]
    total = 0
    for grid in sub_grids:
        puz = Puz(grid)
        for vec, tile in puz.iterate():
            if tile.isupper() and tile.lower() not in puz.all_keys:
                puz.grid[vec.y][vec.x] = '.'
        puz = Puz(grid)  # to reinitialise...
        total += puz.min_path()
    return total


def main():
    text = open('input.txt').read()
    grid = [list(line) for line in text.splitlines()]
    print(solve_1(grid))
    print(solve_2(grid))


if __name__ == "__main__":
    main()
