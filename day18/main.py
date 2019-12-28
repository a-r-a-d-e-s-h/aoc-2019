from collections import defaultdict

filename = "test1.txt"

class Vec(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, vec):
        return Vec(*map(sum, zip(self, vec)))

    def __sub__(self, vec):
        return Vec(*map(lambda x, y: x - y, self, vec))

    def __neg__(self):
        return Vec(*map(lambda x: -x, self))


class Puz:
    DIRECTIONS = [Vec(0, 1), Vec(0, -1), Vec(1, 0), Vec(-1, 0)]
    def __init__(self, grid):
        self._grid = grid
        self.get_pos()
        self.compute_distance_tables()

    def __str__(self):
        return '\n'.join(''.join(row) for row in self._grid)

    def is_key(self, x, y):
        return self.grid(x, y).islower()

    def is_door(self, x, y):
        return self.grid(x, y).isupper()

    def grid(self, x, y):
        return self._grid[y][x]

    def set_grid(self, x, y, val):
        self._grid[y][x] = val

    def get_pos(self):
        for y, row in enumerate(self._grid):
            for x, tile in enumerate(row):
                if tile == '@':
                    self.pos = Vec(x, y)
                    self.set_grid(x, y, '.')


    def on_grid(self, x, y):
        try:
            self.grid(x, y)
        except IndexError:
            return False
        else:
            return True

    def accessible_keys_from(self, pos, have_keys):
        to_do = [pos]
        doors = list(map(str.upper, have_keys))
        min_distances = {}
        keys = {}
        locations = {}
        min_distances[pos] = 0
        while to_do:
            next_to_do = []
            for vec in to_do:
                this_dist = min_distances[vec]
                for direction in self.DIRECTIONS:
                    test_vec = vec + direction
                    if self.on_grid(*test_vec):
                        tile = self.grid(*test_vec)
                        if tile == '.' or tile.islower() or tile in doors:
                            if test_vec not in min_distances:
                                min_distances[test_vec] = this_dist + 1
                                next_to_do.append(test_vec)
                                if tile != '.' and tile not in have_keys and tile not in doors:
                                    keys[tile] = this_dist + 1
                                    locations[tile] = test_vec
                pass
            to_do = next_to_do
        return {'dists': keys, 'locations': locations}

    def collect_all_keys(self):
        key_realms = {(): KeyRealm(self._grid, ())}


    def count_keys_and_doors(self):
        keys = doors = 0
        for row in self._grid:
            for tile in row:
                if tile.islower():
                    keys += 1
                elif tile.isupper():
                    doors += 1
        return (keys, doors)

    def openable_doors(self):
        res = self.accessible_keys_and_distances()
        keys = res['keys']
        doors = res['doors']
        ret = []
        for door in doors.keys():
            if door.lower() in keys:
                ret.append(door)
        return ret

    def open_door(self, door):
        for y, row in enumerate(self._grid):
            for x, tile in enumerate(row):
                if self.grid(x, y) == door:
                    self.set_grid(x, y, '.')

    def min_path(self):
        self.best_found = float('inf')
        self.min_from(self.pos, (), 0)
        return self.best_found

    def min_from(self, pos, keys, running_tot):
        # We have the keys stored in keys
        if len(keys) < 15:
            print("investigating:", keys)
        remaining_keys = tuple(key for key in self.all_keys if key not in keys)
        lower_bound = 0
        for key in remaining_keys:
            lower_bound = max(lower_bound, self.lookup[key][pos])
        if running_tot + lower_bound >= self.best_found:
            # No point in continuing.
            return

        accessible = self.accessible_keys_from(pos, keys)
        dists = accessible['dists']
        locations = accessible['locations']
        if not dists: # we have visited every key!
            if running_tot < self.best_found:
                print(running_tot)
                self.best_found = running_tot
            else:
                print("{} <= {}".format(self.best_found, running_tot))
            return
        for key in dists.keys():
            if dists[key] + running_tot >= self.best_found:
                continue # skip this
            self.min_from(locations[key],
                          keys + (key,),
                          running_tot + dists[key])

    def compute_distance_tables(self):
        # For each key, calculate distance to it from every square, treating
        # this keys own door as locked, but all others open. This is always a
        # lower bound given any position, for any uncollected key.
        keys_with_pos = {}
        doors_with_pos = {}
        all_paths = []
        for y, row in enumerate(self._grid):
            for x, tile in enumerate(row):
                if tile.islower():
                    keys_with_pos[tile] = Vec(x, y)
                elif tile.isupper():
                    doors_with_pos[tile] = Vec(x, y)
                if tile != '#':
                    all_paths.append(Vec(x, y))
        lookup_for_key = {}
        all_keys = tuple(sorted(keys_with_pos.keys()))
        self.all_keys = all_keys
        blank_grid = []
        for row in self._grid:
            new_row = []
            for tile in row:
                if tile == '#':
                    new_row.append('#')
                else:
                    new_row.append('.')
            blank_grid.append(new_row)

        for this_key in all_keys:
            key_pos = keys_with_pos[this_key]
            door_pos = doors_with_pos[this_key.upper()]
            lookup = {key_pos: 0}
            lookup_for_key[this_key] = lookup
            to_do = [key_pos]
            while to_do:
                new_to_do = []
                while to_do:
                    vec = to_do.pop()
                    for direction in self.DIRECTIONS:
                        test_vec = vec + direction
                        x, y = test_vec
                        if all((
                            test_vec not in lookup,
                            blank_grid[y][x] == '.',
                            test_vec != door_pos
                        )):
                            lookup[test_vec] = lookup[vec] + 1
                            to_do.append(test_vec)
                new_to_do = to_do

        self.lookup = lookup_for_key


def solve_1(puz):
    return puz.min_path()



def main():
    with open(filename) as f:
        lines = f.read().splitlines()
        lines = [l for l in lines if l]
    grid = [list(line) for line in lines]
    puz = Puz(grid)
    solve_1(puz)


main()
