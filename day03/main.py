def parse_input(text):
    return [parse_wire(line) for line in text.splitlines() if line]

def parse_instructions(text):
    items = text.split(',')
    items = [item for item in items if item.strip()]
    steps = []
    for item in items:
        steps.append((item[0], int(item[1:])))
    return steps

DIRECTIONS = {
    'R': (1, 0),
    'L': (-1, 0),
    'U': (0, 1),
    'D': (0, -1)
}

def plot_path(wire, start=(0, 0)):
    plot = {}
    pos = start
    steps = 0
    for step in wire:
        d = DIRECTIONS[step[0]]
        for i in range(step[1]):
            steps += 1
            pos = tuple(map(sum, zip(pos, d)))
            plot[pos] = steps
    return plot


def solve_1(b0, b1):
    intersection_dists = [sum(map(abs, coord)) for coord in b0 if coord in b1]
    return min(intersection_dists)


def solve_2(b0, b1):
    intersection_dists = [b0[coord] + b1[coord] for coord in b0 if coord in b1]
    return min(intersection_dists)

path_instructions = [parse_instructions(line) for line in open('input.txt')]
paths = [plot_path(instructions) for instructions in path_instructions]
print(solve_1(*paths))
print(solve_2(*paths))
