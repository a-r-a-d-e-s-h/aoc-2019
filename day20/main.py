class Vec(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, vec):
        return Vec(*map(sum, zip(self, vec)))

    def __sub__(self, vec):
        return Vec(*map(lambda x, y: x - y, self, vec))

    def __neg__(self):
        return Vec(*map(lambda x: -x, self))

class Maze:
    DIRECTIONS = [Vec(0, 1), Vec(0, -1), Vec(1, 0), Vec(-1, 0)]

    def __init__(self, grid):
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)
        self.init_portals()


    def init_portals(self):
        from collections import defaultdict
        portals = defaultdict(list)
        # Verticals:
        for y, row in enumerate(self.grid):
            outer = y in (0, self.height - 3)
            if y == self.height - 2:
                break
            for x, tile in enumerate(row):
                if all((tile.isalpha(),
                        self.grid[y + 1][x].isalpha(),
                        self.grid[y + 2][x] == '.')):
                    name = tile + self.grid[y + 1][x]
                    portals[name].append({
                        'source': Vec(x, y + 1),
                        'target': Vec(x, y + 2),
                        'outer': outer
                    })
                elif all((tile == '.',
                          self.grid[y + 1][x].isalpha(),
                          self.grid[y + 2][x].isalpha())):
                    name = self.grid[y + 1][x] + self.grid[y + 2][x]
                    portals[name].append({
                        'source': Vec(x, y + 1),
                        'target': Vec(x, y),
                        'outer': outer
                    })
        # Horizontals:
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                outer = (x == 0 or x == self.width - 3)
                if x == self.width - 2:
                    break
                tiles = self.grid[y][x:x+3]
                if tiles[0].isalpha() and tiles[1].isalpha() and tiles[2] == '.':
                    name = ''.join(tiles[0:2])
                    portals[name].append({
                        'source': Vec(x + 1, y),
                        'target': Vec(x + 2, y),
                        'outer': outer
                    })
                elif tiles[0] == '.' and tiles[1].isalpha() and tiles[2].isalpha():
                    name = ''.join(tiles[1:3])
                    portals[name].append({
                        'source': Vec(x + 1, y),
                        'target': Vec(x, y),
                        'outer': outer
                    })
        self.portals = portals

    def move_to(self, pos):
        if self.grid[pos[1]][pos[0]] == '.':
            return pos
        else:
            for portal_name, portals in self.portals.items():
                if len(portals) == 2:
                    p1, p2 = portals
                    if p1['source'] == pos:
                        return p2['target']
                    if p2['source'] == pos:
                        return p1['target']
        return pos

    def move_with_realm(self, pos, realm):
        if self.grid[pos[1]][pos[0]] == '.':
            return pos, realm
        else:
            for portal_name, portals in self.portals.items():
                if len(portals) == 2:
                    p1, p2 = portals
                    if p1['source'] == pos:
                        if p1['outer']:
                            if realm > 0:
                                return p2['target'], realm - 1
                        else:
                            return p2['target'], realm + 1
                    if p2['source'] == pos:
                        if p2['outer']:
                            if realm > 0:
                                return p1['target'], realm - 1
                        else:
                            return p1['target'], realm + 1
        return pos, realm



def solve_1(grid):
    maze = Maze(grid)
    start = maze.portals["AA"][0]['target']
    goal = maze.portals['ZZ'][0]['target']

    distances = {start: 0}
    to_do = [start]
    while to_do:
        new_to_do = []
        while to_do:
            vec = to_do.pop(0)
            for direc in maze.DIRECTIONS:
                x, y = test_vec = maze.move_to(vec + direc)
                if all((grid[y][x] == '.',
                        test_vec not in distances)):
                    distances[test_vec] = distances[vec] + 1
                    new_to_do.append(test_vec)
        to_do = new_to_do
    return distances[goal]


def solve_2(grid):
    maze = Maze(grid)
    start = maze.portals["AA"][0]['target'], 0
    end = maze.portals["ZZ"][0]['target'], 0
    print(start, end)

    distances = {start: 0}
    from bisect import bisect_left
    from collections import deque
    distance_keys = deque([start])
    distance_values = deque([0])
    to_do = [start]
    counter = 0
    while to_do:
        print(counter)
        counter += 1
        new_to_do = []
        while to_do:
            vec, realm = to_do.pop()
            for direc in maze.DIRECTIONS:
                test_vec, test_realm = maze.move_with_realm(vec + direc, realm)
                if test_vec == end[0] and test_realm == 0:
                    index = bisect_left(distance_keys, (vec, realm))
                    return distance_values[index] + 1
                x, y = test_vec
                index = bisect_left(distance_keys, (test_vec, test_realm))
                check_passed = False
                if index >= len(distance_keys):
                    check_passed = True
                else:
                    if distance_keys[index] != (test_vec, test_realm):
                        check_passed = True
                if grid[y][x] == '.' and check_passed:
                    old_dist_index = bisect_left(distance_keys, (vec, realm))
                    old_dist = distance_values[old_dist_index]
                    distance_keys.insert(index, (test_vec, test_realm))
                    distance_values.insert(index, old_dist + 1)
                    new_to_do.append((test_vec, test_realm))
        to_do = new_to_do



def main():
    text = open("input.txt").read()
    lines = text.splitlines()
    grid = [list(line) for line in lines if line]

    #print(solve_1(grid))
    print(solve_2(grid))
#    maze = Maze(grid)
#    outer_portal_targets = []
#    for portal_name, portals in maze.portals.items():
#        for portal in portals:
#            if portal['outer']:
#                outer_portal_targets.append(portal['target'])
#    for y, row in enumerate(grid):
#        if y > 10:
#            break
#        for x, tile in enumerate(row):
#            if (x, y) in outer_portal_targets:
#                print("@", end='')
#            else:
#                print(tile, end='')
#        print()





main()
