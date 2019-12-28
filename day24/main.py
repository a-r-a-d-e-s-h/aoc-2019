from bisect import bisect_left
from collections import deque

class Puz:
    def __init__(self, filename):
        self.load(filename)

    def load(self, fn):
        self.grid = open(fn).read().splitlines()
        self.width = len(self.grid[0])
        self.height = len(self.grid)


    def neighbours_adj(self, x, y):
        for _y in (y - 1, y + 1):
            if 0 <= _y < self.height:
                yield (x, _y)
        for _x in (x - 1, x + 1):
            if 0 <= _x < self.width:
                yield (_x, y)

    def iter_grid(self):
        new_grid = []
        for y, row in enumerate(self.grid):
            new_row = []
            for x, tile in enumerate(row):
                bugs = 0
                for (_x, _y) in self.neighbours_adj(x, y):
                    bugs += self.grid[_y][_x] == '#'
                if tile == '#':
                    if bugs != 1:
                        new_row.append('.')
                    else:
                        new_row.append('#')
                else:
                    if 1 <= bugs <= 2:
                        new_row.append('#')
                    else:
                        new_row.append('.')
            new_grid.append(''.join(new_row))
        self.grid = new_grid

    def __str__(self):
        return '\n'.join(self.grid)
                
    def to_tuple(self):
        the_list = []
        for row in self.grid:
            the_list.extend(row)
        return tuple(the_list)


def solve_1(filename):
    puz = Puz(filename)
    patterns = deque()
    while 1:
        tup = puz.to_tuple()
        num_patterns = len(patterns)
        index = bisect_left(patterns, tup)
        if index >= num_patterns:
            patterns.append(tup)
        else:
            if patterns[index] != tup:
                patterns.insert(index, tup)
            else:
                break

        res = puz.iter_grid()
    tot = 0
    for x in range(puz.width):
        for y in range(puz.height):
            index = x + y*puz.width
            if puz.grid[y][x] == '#':
                tot += 2**index
    return tot


class PuzRecursive:
    # Set of neighbours for each tile. have keys (x, y) coordinates, and each
    # value is a tuple of the neighbours we consider. Each neighbour is
    # represented by a tuple of the form (d, (u, v)) where d represents a grid
    # offset and (u, v) a coordinate on the corresponding grid. For example,
    # d=0 indicates the same grid, d=-1, the outer grid, and d=1, the inner
    # grid.
    neighbours = {
        # Corners:
        (0, 0): ((-1, (2, 1)),
                 (-1, (1, 2)),
                 (0, (1, 0)),
                 (0, (0, 1))),
        (4, 0): ((-1, (2, 1)),
                 (-1, (3, 2)),
                 (0, (3, 0)),
                 (0, (4, 1))),
        (0, 4): ((-1, (1, 2)),
                 (-1, (2, 3)),
                 (0, (0, 3)),
                 (0, (1, 4))),
        (4, 4): ((-1, (3, 2)),
                 (-1, (2, 3)),
                 (0, (4, 3)),
                 (0, (3, 4))),
        # Edges
        (1, 0): ((-1, (2, 1)),
                 (0, (0, 0,)),
                 (0, (2, 0)),
                 (0, (1, 1))),
        (2, 0): ((-1, (2, 1)),
                 (0, (1, 0)),
                 (0, (3, 0)),
                 (0, (2, 1))),
        (3, 0): ((-1, (2, 1)),
                 (0, (2, 0)),
                 (0, (4, 0)),
                 (0, (3, 1))),
        (0, 1): ((-1, (1, 2)),
                 (0, (0, 0)),
                 (0, (1, 1)),
                 (0, (0, 2))),
        (0, 2): ((-1, (1, 2)),
                 (0, (0, 1)),
                 (0, (1, 2)),
                 (0, (0, 3))),
        (0, 3): ((-1, (1, 2)),
                 (0, (0, 2)),
                 (0, (1, 3)),
                 (0, (0, 4))),
        (4, 1): ((-1, (3, 2)),
                 (0, (4, 0)),
                 (0, (3, 1)),
                 (0, (4, 2))),
        (4, 2): ((-1, (3, 2)),
                 (0, (4, 1)),
                 (0, (3, 2)),
                 (0, (4, 3))),
        (4, 3): ((-1, (3, 2)),
                 (0, (4, 2)),
                 (0, (3, 3)),
                 (0, (4, 4))),
        (1, 4): ((-1, (2, 3)),
                 (0, (1, 3)),
                 (0, (0, 4)),
                 (0, (2, 4))),
        (2, 4): ((-1, (2, 3)),
                 (0, (1, 4)),
                 (0, (2, 3)),
                 (0, (3, 4))),
        (3, 4): ((-1, (2, 3)),
                 (0, (2, 4)),
                 (0, (3, 3)),
                 (0, (4, 4))),
        # bordering center tile
        (2, 1):
            ((0, (2, 0)), (0, (1, 1)), (0, (3, 1)),
             (1, (0, 0)), (1, (1, 0)), (1, (2, 0)), (1, (3, 0)), (1, (4, 0))),
        (1, 2):
            ((0, (1, 1)), (0, (0, 2)), (0, (1, 3)),
             (1, (0, 0)), (1, (0, 1)), (1, (0, 2)), (1, (0, 3)), (1, (0, 4))),
        (3, 2):
            ((0, (3, 1)), (0, (4, 2)), (0, (3, 3)),
             (1, (4, 0)), (1, (4, 1)), (1, (4, 2)), (1, (4, 3)), (1, (4, 4))),
        (2, 3):
            ((0, (1, 3)), (0, (2, 4)), (0, (3, 3)),
             (1, (0, 4)), (1, (1, 4)), (1, (2, 4)), (1, (3, 4)), (1, (4, 4))),
        # remaining non-special tiles:
        (1, 1): ((0, (1, 0)), (0, (0, 1)), (0, (2, 1)), (0, (1, 2))),
        (3, 1): ((0, (3, 0)), (0, (2, 1)), (0, (4, 1)), (0, (3, 2))),
        (1, 3): ((0, (0, 3)), (0, (1, 2)), (0, (2, 3)), (0, (1, 4))),
        (3, 3): ((0, (3, 2)), (0, (2, 3)), (0, (4, 3)), (0, (3, 4))),
        # center:
        (2, 2): ()
    }
    def __init__(self, filename):
        self.load(filename)

    def load(self, filename):
        grid = open(filename).read().splitlines()
        self.height = len(grid)
        self.width = len(grid[0])
        self.grids = deque([grid])
        assert self.width == 5
        assert self.height == 5


    def iter_grids(self):
        # First we add new grids to the start and end, and scrap them if they
        # get no new bugs
        self.grids.appendleft(['.'*self.width]*self.height)
        self.grids.append(['.'*self.width]*self.height)
        total_grids = len(self.grids)
        new_grids = deque()
        for i, grid in enumerate(self.grids):
            new_grid = []
            for y in range(self.height):
                new_row = []
                for x in range(self.width):
                    bug_neighbours = 0
                    tile = grid[y][x]
                    for d, (_x, _y) in self.neighbours[x, y]:
                        index = d + i
                        if 0 <= index < len(self.grids):
                            bug_neighbours += self.grids[index][_y][_x] == '#'
                    if tile == '#':
                        if bug_neighbours == 1:
                            new_row.append('#')
                        else:
                            new_row.append('.')
                    else:
                        if 1 <= bug_neighbours <= 2:
                            new_row.append('#')
                        else:
                            new_row.append('.')
                new_grid.append(''.join(new_row))
            new_grids.append(new_grid)
        grid = new_grids[0]
        if not any('#' in row for row in grid):
            new_grids.popleft()
        grid = new_grids[-1]
        if not any('#' in row for row in grid):
            new_grids.pop()
        self.grids = new_grids


def solve_2(filename):
    puz = PuzRecursive(filename)
    for __ in range(200):
        puz.iter_grids()
    total = 0
    for grid in puz.grids:
        for row in grid:
            for tile in row:
                total += tile == '#'
    return total


def main():
    filename = "input.txt"
    print(solve_1(filename))
    print(solve_2(filename))


if __name__ == "__main__":
    main()
