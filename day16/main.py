from itertools import cycle

filename = 'input.txt'

class Puz:
    base_pattern = (0, 1, 0, -1)
    def __init__(self, filename):
        self.data = open(filename).read()
        self.length = len(self.data)

    def iter_digits(self):
        for char in self.data:
            yield int(char)

    def sum_and_multiply(self, phase, pattern):
        return sum(x*y for x, y in zip(phase, pattern))

    def _pattern_from_base(self, base, index):
        for item in base:
            for __ in range(index):
                yield item

    def pattern_from_base(self, index):
        the_iter = self._pattern_from_base(self.base_pattern, index + 1)
        the_iter = cycle(the_iter)
        next(the_iter)
        return the_iter

    def calc_for_phase(self, phase):
        ret = []
        for i in range(len(phase)):
            val = self.calc_with_index(phase, i)
            ret.append(abs(val) % 10)
        return ret

    def calc_with_index(self, phase, index):
        pat = self.pattern_from_base(index)
        return self.sum_and_multiply(phase, pat)

def solve_1(filename):
    puz = Puz(filename)
    phase = list(puz.iter_digits())
    for i in range(100):
        phase = puz.calc_for_phase(phase)
    return ''.join(map(str, phase[:8]))


def build_partial_sum_array(a):
    # have an array of integers of length n that we cycle
    # build an nxn array so that array[i][j]
    # is the sum of (i+1) consecutive terms starting from a[j]
    # and cycling round if necessary

    n = len(a)
    array = [[0]*n for __ in range(n)]
    double_a = a + a
    for i in range(n):
        new_row = []
        for j in range(n):
            if i == 0:
                array[i][j] = a[j]
            else:
                array[i][j] = a[i-1][j] + double_a[j + i]
    return build_partial_sum_array(a)


def get_digit(n):
    return abs(n) % 10

def solve_2(base_seq, repeats, offset, iterations):
    base_len = len(base_seq)
    full_length = base_len * repeats
    if offset < (full_length + 1)//2:
        raise NotImplementedError("This method only works for offset"
                                  " sufficiently large.")
    # We need the sequence repeating from the offset
    counter = offset
    seq = []
    for i in range(offset, full_length):
        seq.append(base_seq[i % base_len])

    seq_len = len(seq)
    for __ in range(iterations):
        for i in range(1, seq_len):
            seq[seq_len - 1 - i] += seq[seq_len - i]

        seq = list(map(get_digit, seq))
    return ''.join(map(str, seq[:8]))


def main():
    digits = list(map(int, open(filename).read()))
    print(solve_1(filename))
    offset = int(''.join(map(str, digits[:7])))
    print(solve_2(digits, 10000, offset, 100))

main()
