from collections import defaultdict
from math import ceil
import re

filename = 'input.txt'

class Chemical:
    multiples_of = 0
    requires = None

    def __init__(self, name):
        self.name = name


class Puzzle:
    def __init__(self, filename):
        self.filename = filename
        self.reset()

    def reset(self):
        self.chemicals = {}
        self.reactions = []
        self.load_data()

    def load_data(self):
        for line in open(self.filename):
            left_part, right_part = line.split('=>')
            l_items = re.findall('-?\d+ [A-Z]+', left_part)
            r_items = re.findall('-?\d+ [A-Z]+', right_part)
            l_items = list(map(self.parse_item, l_items))
            r_items = list(map(self.parse_item, r_items))
            assert len(r_items) == 1
            self.reactions.append((l_items, r_items))
            r_chem = r_items[0][1]
            r_chem.multiples_of = r_items[0][0]
            r_chem.requires = l_items


    def parse_item(self, item):
        val, name = item.split(' ')
        val = int(val)
        return (val, self.get_chemical(name))

    def min_source_needed_for_target(
            self, source, target, n, storage=defaultdict(int)):
        # How many of 'source' do we need to produce at least n targets.
        target = self.get_chemical(target)
        source = self.get_chemical(source)
        if target in storage:
            in_storage = storage[target]
            if in_storage >= n:
                storage[target] -= n
                n = 0
            else:
                n -= storage[target]
                storage[target] = 0
        if target == source:
            return n

        m = target.multiples_of
        needed_for_m = 0
        
        for count, chem in target.requires:
            needed_for_m += self.min_source_needed_for_target(
                source,
                chem,
                count*(ceil(n/m)),
                storage
            )
        storage[target] += ceil(n/m)*m - n

        return needed_for_m

    def get_chemical(self, name):
        if isinstance(name, Chemical):
            return name
        if name not in self.chemicals:
            self.chemicals[name] = Chemical(name)
        return self.chemicals[name]



def solve_1(puz):
    return puz.min_source_needed_for_target('ORE', 'FUEL', 1)


def solve_2(puz):
    # do a binary search
    target = 1000000000000

    lower_bound = upper_bound = 10000

    while 1:
        puz.reset()
        val = puz.min_source_needed_for_target('ORE', 'FUEL', upper_bound) 
        if target < val:
            break
        else:
            lower_bound = upper_bound
            upper_bound *= 2
    while 1:
        next_guess = (lower_bound + upper_bound)//2
        puz.reset()
        res = puz.min_source_needed_for_target('ORE', 'FUEL', next_guess)
        if res <= target:
            lower_bound = next_guess
        else:
            upper_bound = next_guess
        if lower_bound == upper_bound - 1:
            return lower_bound


def main():
    puz = Puzzle(filename)
    print(solve_1(puz))
    print(solve_2(puz))

main()
