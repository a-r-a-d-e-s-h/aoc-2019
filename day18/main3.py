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
    def __init__(self, grid):
        self.grid = grid
        self.init_keys()
        self.start = self.find_start()

    def enumerate(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                yield Vec(x, y), tile

    def init_keys(self):
        self.keys = {}
        for vec, tile in self.enumerate():
            if tile.islower():
                self.keys[tile] = vec

    def find_start(self):
        for vec, tile in self.enumerate():
            if tile == '@':
                return vec

    def is_walkable(self, tile):
        return tile != '#'

    def min_path(self):
        if not self.check_condition():
            raise Exception("Maze of invalid type for this solver.")
        from collections import defaultdict
        distance_table = defaultdict(dict)
        self.distance_table = distance_table
        door_table = defaultdict(dict)
        for start in self.route_info:
            start_tile = self.grid[start.y][start.x]
            for end in self.route_info[start]:
                end_tile = self.grid[end.y][end.x]
                route = self.route_info
                path = self.route_info[start][end]
                distance_table[start_tile][end_tile] = len(path)
                doors = []
                for vec in path:
                    tile = self.grid[vec.y][vec.x]
                    if tile.isupper():
                        doors.append(tile)
                door_table[start_tile][end_tile] = doors

        self.optimal_sol = float('inf')
        all_keys = list(self.keys.keys())
        total_keys = len(all_keys)
        def recursive_solve(start, keys, running_total):
            doors = door_table[start]
            num_keys = len(keys)
            if num_keys < 10:
                print(self.optimal_sol, keys)
            if num_keys == total_keys:
                if running_total < self.optimal_sol:
                    print("{} -> {}".format(self.optimal_sol, running_total))
                    self.optimal_sol = running_total
            else:
                lower_bound = self.lower_bound(start, keys)
                if running_total + lower_bound >= self.optimal_sol:
                    return
            # Find the onesto investigate
            to_investigate = []
            for key in doors:
                if all(door.lower() in keys for door in doors[key]):
                    # can access key
                    if key in keys:
                        continue
                    dist = distance_table[start][key]
                    to_investigate.append((dist, (key,
                                                  keys + (key,),
                                                  running_total + dist)))
            to_investigate.sort()
            for dist, args in to_investigate:
                recursive_solve(*args)
        recursive_solve('@', (), 0)
        return self.optimal_sol

    def lower_bound(self, tile, keys):
        min_required = float('inf')

        for key in self.keys:
            if key in keys:
                continue
            dist = self.distance_table[tile][key]
            min_required = min(min_required, dist)
        return min_required



    def check_condition(self):
        self.find_routes()
        route_info = self.route_info
        for start in route_info:
            for end in route_info[start]:
                path = route_info[start][end]
                doors = []
                for vec in path:
                    tile = self.grid[vec.y][vec.x]
                    if tile.isupper():
                        doors.append(tile)
                for door in doors:
                    path = self.find_route(start, end, (door,))
                    if path is not None:
                        return False
        return True

    def find_routes(self):
        points = [self.start]
        points.extend(self.keys.values())
        route_info = {}
        for point in points:
            route_info[point] = self.find_routes_from(point, points)
        self.route_info = route_info

    def find_routes_from(self, start, points):
        routes = {}
        for point in points:
            if point != self.start:
                routes[point] = self.find_route_between(start, point)
        return routes

    def find_route_between(self, start, end):
        return self.find_route(start, end, locked=())

    def find_route(self, start, end, locked):
        to_do = [end]
        children = {end: None}

        while to_do:
            new_to_do = []
            while to_do:
                vec = to_do.pop()
                for d in self.DIRECTIONS:
                    test_vec = vec + d
                    test_tile = self.grid[test_vec.y][test_vec.x]
                    if all((self.is_walkable(test_tile),
                            test_vec not in children,
                            test_tile not in locked)):
                        new_to_do.append(test_vec)
                        children[test_vec] = vec
            to_do = new_to_do
        if start not in children:  # No valid route
            return None

        path = []
        pos = start
        while 1:
            pos = children.get(pos, None)
            if pos is None:
                break
            path.append(pos)
        return path

def solve_1(grid):
    puz = Puz(grid)
    return puz.min_path()


def main():
    text = open('test4.txt').read()
    grid = [list(line) for line in text.splitlines()]
    import time
    start = time.time()
    print(solve_1(grid))
    print("elapsed: {:.2f}s".format(time.time() - start))


if __name__ == "__main__":
    main()
