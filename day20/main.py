from collections import defaultdict, namedtuple
from itertools import chain
import re


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


class Maze:
    DIRECTIONS = [Vec(0, 1), Vec(0, -1), Vec(1, 0), Vec(-1, 0)]
    Portal = namedtuple(
        "Portal",
        (
            'name',    # The 2 character name of the portal
            'source',  # The location off the grid that one walks into
            'target',  # The square on the grid one is teleported to
            'outer'    # Boolean indicating an outer or inner portal
        )
    )

    def __init__(self, grid):
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)
        self.init_portals()

    def init_portals(self):
        """
        Identify the portals names, and locations.

        We search the whole grid for portal names in differnt orientations,
        record their location, and the tile they join to, and keep track of
        whether they are "outer" or "inner" portals.
        """
        portals = defaultdict(list)
        # Verticals:
        for x, col in enumerate(map(''.join, zip(*self.grid))):
            for y, tile in enumerate(col[:-2]):
                outer = y in (0, self.height - 3)
                tiles = col[y:y+3]
                if re.match("[A-Z]{2}\.", tiles):
                    name = tiles[:2]
                    portals[name].append(self.Portal(
                        name=name,
                        source=Vec(x, y + 1),
                        target=Vec(x, y + 2),
                        outer=outer
                    ))
                elif re.match("\.[A-Z]{2}", tiles):
                    name = tiles[1:]
                    portals[name].append(self.Portal(
                        name=name,
                        source=Vec(x, y + 1),
                        target=Vec(x, y),
                        outer=outer
                    ))
        # Horizontals:
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row[:-2]):
                outer = (x == 0 or x == self.width - 3)
                tiles = row[x:x+3]
                if re.match("[A-Z]{2}\.", tiles):
                    name = tiles[:2]
                    portals[name].append(self.Portal(
                        name=name,
                        source=Vec(x + 1, y),
                        target=Vec(x + 2, y),
                        outer=outer
                    ))
                elif re.match("\.[A-Z]{2}", tiles):
                    name = ''.join(tiles[1:])
                    portals[name].append(self.Portal(
                        name=name,
                        source=Vec(x + 1, y),
                        target=Vec(x, y),
                        outer=outer
                    ))
        self.portals = portals

    def move_to(self, pos):
        if self.grid[pos[1]][pos[0]] == '.':
            return pos
        else:
            for portal_name, portals in self.portals.items():
                if len(portals) == 2:
                    p1, p2 = portals
                    if p1.source == pos:
                        return p2.target
                    if p2.source == pos:
                        return p1.target
        return pos

    def move_with_realm(self, pos, realm):
        if self.grid[pos[1]][pos[0]] == '.':
            return pos, realm
        else:
            for portal_name, portals in self.portals.items():
                if len(portals) == 2:
                    p1, p2 = portals
                    if p1.source == pos:
                        if p1.outer:
                            if realm > 0:
                                return p2.target, realm - 1
                        else:
                            return p2.target, realm + 1
                    if p2.source == pos:
                        if p2.outer:
                            if realm > 0:
                                return p1.target, realm - 1
                        else:
                            return p1.target, realm + 1
        return pos, realm

    def plot_connections(self):
        """Calculate accessible portals by walking alone."""
        portal_sources = {}
        all_portals = list(chain.from_iterable(self.portals.values()))
        for portal in all_portals:
            portal_sources[portal.source] = portal

        distance_tables = {}

        for portal in all_portals:
            # Map the routes from each portal in a brute force way
            start = portal.target
            to_do = [start]
            distances = {start: 0}
            accessible_portals = {}
            while to_do:
                new_to_do = []
                for coord in to_do:
                    for direction in self.DIRECTIONS:
                        test_vec = coord + direction
                        test_tile = self.grid[test_vec.y][test_vec.x]
                        if test_vec not in distances:
                            new_dist = distances[coord] + 1
                            if test_vec in portal_sources:
                                new_portal = portal_sources[test_vec]
                                if new_portal != portal:
                                    accessible_portals[new_portal] = new_dist
                                distances[test_vec] = new_dist
                            elif test_tile == '.':
                                distances[test_vec] = new_dist
                                new_to_do.append(test_vec)
                to_do = new_to_do
            distance_tables[portal] = accessible_portals

        self.distance_tables = distance_tables

    def portal_pair(self, portal):
        name = portal.name
        portals = self.portals[name]
        for p in portals:
            if p != portal:
                return p
        return None


def solve_1(grid):
    maze = Maze(grid)
    maze.plot_connections()
    start_portal = maze.portals['AA'][0]
    goal_portal = maze.portals['ZZ'][0]

    distances = defaultdict(list, {0: [start_portal]})
    portals_reached = {start_portal: 1}
    distance = 0
    while 1:
        for item in distances[distance]:
            accessible = maze.distance_tables[item]
            for portal, dist in accessible.items():
                other_portal = maze.portal_pair(portal)

                if portal not in portals_reached:
                    new_dist = dist + distance
                    portals_reached[portal] = new_dist
                    distances[new_dist].append(other_portal)
                    if portal == goal_portal:
                        return new_dist - 1
        distance += 1


def solve_2(grid):
    maze = Maze(grid)
    maze.plot_connections()

    PortalInstance = namedtuple("PortalInstance", (
        "portal",  # Particular portal
        "depth"    # Depth in the recursion. 0 is outermost
    ))

    start_portal = PortalInstance(maze.portals['AA'][0], 0)
    goal_portal = PortalInstance(maze.portals['ZZ'][0], 0)

    distances = defaultdict(list, {0: [start_portal]})
    portals_reached = {start_portal: 1}
    distance = 0
    while 1:
        for item in distances[distance]:
            portal = item.portal
            depth = item.depth

            accessible = maze.distance_tables[portal]
            for portal, dist in accessible.items():
                other_portal = maze.portal_pair(portal)
                if portal.outer:
                    new_depth = depth - 1
                else:
                    new_depth = depth + 1

                if portal not in portals_reached:
                    new_dist = dist + distance
                    portals_reached[PortalInstance(portal, depth)] = new_dist
                    if new_depth >= 0 and other_portal:
                        new_instance = PortalInstance(other_portal, new_depth)
                        distances[new_dist].append(new_instance)
                    if PortalInstance(portal, depth) == goal_portal:
                        return new_dist - 1
        distance += 1


def main():
    text = open("input.txt").read()
    lines = text.splitlines()
    grid = lines

    import time
    start = time.time()
    print(solve_1(grid))
    print(solve_2(grid))


if __name__ == "__main__":
    main()
