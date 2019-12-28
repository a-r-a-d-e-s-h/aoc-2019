from collections import deque
from bisect import bisect_left

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
    visited_locations = None
    distances = None

    def __init__(self, grid):
        self.grid = grid
        self.find_walkable_squares()
        self.find_keys_and_doors()
        self.total_keys = len(self.keys)
        self.start_pos = self.find_start()

    def enum_grid(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                yield(Vec(x, y), tile)

    def find_walkable_squares(self):
        self.walkable_squares = []
        for vec, tile in self.enum_grid():
            if tile in ['@', '.'] or tile.isalpha():
                self.walkable_squares.append(vec)

    def find_keys_and_doors(self):
        self.doors = {}
        self.keys = {}
        for vec, tile in self.enum_grid():
            if tile.isupper():
                self.doors[tile] = vec
            elif tile.islower():
                self.keys[tile] = vec

    def find_start(self):
        for vec, tile in self.enum_grid():
            if tile == '@':
                return vec
        return None

    def min_path(self):
        start_pos = ((), self.start_pos) # first element is our keys
        return self.min_path_compute(*start_pos)

    def is_walkable(self, vec):
        tile = self.grid[vec.y][vec.x]
        return tile != '#'

    def distance_and_index(self, keys, vec):
        index = bisect_left(self.visited_locations, (keys, vec))
        if index >= len(self.visited_locations):
            return None, index
        else:
            if self.visited_locations[index] == (keys, vec):
                return self.distances[index], index
            else:
                return None, index

    def min_path_compute(self, keys, vec):
        to_do = [(keys, vec)] 
        self.visited_locations = deque(to_do)
        self.distances = deque([0])
        max_key_collection = 0
        distance_so_far = 0
        while to_do:
            print(distance_so_far, len(to_do))
            new_to_do = []
            while to_do:
                keys, vec = to_do.pop()
                orig_dist, index = self.distance_and_index(keys, vec)
                for direction in self.DIRECTIONS:
                    test_vec = vec + direction
                    if self.is_walkable(test_vec):
                        tile = self.grid[test_vec.y][test_vec.x]
                        if tile.isupper() and tile.lower() not in keys:
                            continue  # Cannot proceed! locked door
                        if tile.islower() and tile not in keys:
                            # Found a new key!
                            new_keys = tuple(sorted(keys + (tile,)))
                        else:
                            new_keys = keys

                        dist, index = self.distance_and_index(new_keys,
                                                              test_vec)
                        if dist is None:  # new location
                            key_collection = len(new_keys)
                            if key_collection > max_key_collection:
                                max_key_collection = key_collection
                                print("{}: {}".format(key_collection, new_keys))
                            if key_collection == self.total_keys:
                                return orig_dist + 1
                            self.distances.insert(index, orig_dist + 1)
                            self.visited_locations.insert(
                                index,
                                (new_keys, test_vec)
                            )
                            new_to_do.append((new_keys, test_vec))

            to_do = new_to_do
            distance_so_far += 1



def solve_1(grid):
    puz = Puz(grid)

    return puz.min_path()


def main():
    text = open('test4.txt').read()
    grid = [list(line) for line in text.splitlines()]
    print(solve_1(grid))

if __name__ == "__main__":
    main()
