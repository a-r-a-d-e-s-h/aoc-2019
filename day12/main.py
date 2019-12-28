from collections import deque
import bisect
import re

from itertools import combinations

filename = "input.txt"


class Moon:
    def __init__(self, vector):
        self.vector = vector
        self.velocity = [0] * len(vector)

    def __repr__(self):
        return "<Moon: {}>".format(self.vector)

    def modify_by(self, moon):
        v1, v2 = self.vector, moon.vector
        for i, (x1, x2) in enumerate(zip(v1, v2)):
            if x1 < x2:
                self.velocity[i] += 1
                moon.velocity[i] -= 1
            elif x1 > x2:
                self.velocity[i] -= 1
                moon.velocity[i] += 1

    def apply_modifier(self):
        self.vector = tuple(map(sum, zip(self.vector, self.velocity)))

    @property
    def energy(self):
        return sum(map(abs, self.vector)) * sum(map(abs, self.velocity))

    def as_tuple(self):
        return self.vector + tuple(self.velocity)

def parse_input(filename):
    data = []
    for line in open(filename):
        data.append(tuple(map(int, re.findall("-?\d+", line))))
    return list(map(Moon, data))


def solve_1(moons):
    for i in range(1000):
        for moon1, moon2 in combinations(moons, 2):
            moon1.modify_by(moon2)

        for moon in moons:
            moon.apply_modifier()
    return sum(moon.energy for moon in moons)

def solve_2(moons):
    indices = []
    start = ()
    for coord in range(3):
        start = ()
        for moon in moons:
            start = start + (moon.vector[coord], moon.velocity[coord])
        test_moons = []
        for moon in moons:
            test_moons.append(Moon(moon.vector))

        counter = 0
        while 1:
            tup = ()
            for moon in test_moons:
                tup = tup + (moon.vector[coord], moon.velocity[coord])
            if tup == start and counter:
                break
            for moon1, moon2 in combinations(test_moons, 2):
                moon1.modify_by(moon2)
            for moon in test_moons:
                moon.apply_modifier()
            counter += 1
        indices.append(counter)
    return indices


def gcd(x, y):
    x = abs(x)
    y = abs(y)
    if x <= y:
        if x == 0:
            return y
        return gcd(x, y % x)
    else:
        return gcd(y, x)


def main():
    moons = parse_input(filename)
    print(solve_1(moons))
    moons = parse_input(filename)
    indices = solve_2(moons)
    vals = indices
    res = vals[0] * vals[1]//gcd(vals[0], vals[1])
    res = vals[2] * res // gcd(vals[2], res)
    print(res)


main()
