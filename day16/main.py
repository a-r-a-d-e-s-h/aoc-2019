from itertools import accumulate, chain, count, cycle, islice, repeat, tee
import operator

filename = 'input.txt'


class Puz:
    base_pattern = (0, 1, 0, -1)

    def __init__(self, filename):
        self.data = open(filename).read()
        self.length = len(self.data)

    def iter_digits(self):
        return map(int, self.data)

    def sum_and_multiply(self, phase, pattern):
        return sum(map(operator.mul, phase, pattern))

    def _pattern_from_base(self, base, index):
        def repeater(x):
            return repeat(x, index)
        return chain.from_iterable(map(repeater, base))

    def pattern_from_base(self, index):
        the_iter = self._pattern_from_base(self.base_pattern, index + 1)
        the_iter = cycle(the_iter)
        return islice(the_iter, 1, None)

    def iterate_phase(self, phase):
        for i in range(self.length):
            phase[i] = self.get_digit(self.calc_with_index(phase, i))
        phase[:] = map(self.get_digit, phase)

    def calc_with_index(self, phase, index):
        pat = self.pattern_from_base(index)
        return self.sum_and_multiply(islice(phase, index, None),
                                     islice(pat, index, None))

    def get_digit(self, val):
        return abs(val) % 10


def solve_1(filename):
    puz = Puz(filename)
    phase = list(puz.iter_digits())
    for i in range(100):
        puz.iterate_phase(phase)
    return ''.join(map(str, islice(phase, 8)))


def solve_2(base_seq, repeats, offset, iterations):
    base_len = len(base_seq)
    full_length = base_len * repeats
    if offset < (full_length + 1)//2:
        raise NotImplementedError(
            "This method only works for offset sufficiently large."
        )
    # We need the sequence repeating from the offset
    seq = []
    for i in range(offset, full_length):
        seq.append(base_seq[i % base_len])

    seq.reverse()
    for __ in range(iterations):
        seq = accumulate(seq)

    def get_digit(n):
        return abs(n) % 10

    seq = map(get_digit, seq)
    seq = list(seq)
    seq.reverse()
    return ''.join(map(str, seq[:8]))


def main():
    import time
    start = time.time()
    print(solve_1(filename))
    print("{:.2f}s".format(time.time() - start))
    digits = list(map(int, open(filename).read()))
    offset = int(''.join(map(str, digits[:7])))
    print(solve_2(digits, 10000, offset, 100))


main()
