from collections import deque, namedtuple
import re


class LinearMapBase:
    modulo = None

    def __init__(self, a, b):
        self.a = a % self.modulo
        self.b = b % self.modulo

    def inverse(self):
        """Assumes that (a, modulo) = 1"""
        s, t = self.euclid(self.b, self.modulo)
        return type(self)(-self.a*s, s)

    def euclid(self, a, b):
        c = b % a
        if c == 0:
            return (1, 0)
        else:
            n = (b - c)//a
            s, t = self.euclid(b - n*a, a)
            return (t - n*s), s

    def compose(self, f):
        return type(self)(self.a + self.b*f.a, self.b * f.b)

    def apply(self, x):
        return (self.a + self.b*x) % self.modulo

class BigDeck:
    class LinearMap(LinearMapBase):
        pass

    def __init__(self, size):
        self.size = size
        self.LinearMap.modulo = size
        self.inverses = {}

    def deal_with_increment(self, d):
        return self.LinearMap(0, d).inverse()

    def cut(self, t):
        return self.LinearMap(t, 1)

    def reverse(self):
        return self.LinearMap(-1, -1)

    def from_line(self, line):
        if line.strip() == "deal into new stack":
            return self.reverse()
        else:
            val = int(re.findall('-?\d+', line)[0])
            if line[0] == 'c':
                return self.cut(val)
            elif line[0] == 'd':
                return self.deal_with_increment(val)
            else:
                raise Exception("unknown case")


def solve_1(filename, size=10007):
    deck = BigDeck(size)
    identity = deck.LinearMap(0, 1)
    cur_map = identity
    lines = open(filename).read().splitlines()
    for line in lines:
        cur_map = cur_map.compose(deck.from_line(line))
    return cur_map.inverse().apply(2019)



def solve_2(filename, size=119315717514047, repeats=101741582076661):
    deck = BigDeck(size)
    lines = open(filename).read().splitlines()
    identity = deck.LinearMap(0, 1)
    cur_map = identity
    for line in lines:
        cur_map = cur_map.compose(deck.from_line(line))

    powers_of_2 = {0: cur_map}
    def get_power(n):
        if n in powers_of_2:
            return powers_of_2[n]
        else:
            powers_of_2[n] = get_power(n-1).compose(get_power(n-1))
            return powers_of_2[n]
    counter = 0
    final_map = identity
    while repeats:
        if repeats % 2:
            final_map = final_map.compose(get_power(counter))
        repeats //= 2
        counter += 1
    return final_map.apply(2020)



def main():
    print(solve_1("input.txt"))
    print(solve_2("input.txt"))


if __name__ == "__main__":
    main()

