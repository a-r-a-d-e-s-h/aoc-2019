def parse_input(text):
    return [parse_wire(line) for line in text.splitlines() if line]

def parse_wire(text):
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

def print_wire(board, wire, start=(0, 0)):
    pos = start
    steps = 0
    for step in wire:
        d = DIRECTIONS[step[0]]
        for i in range(step[1]):
            steps += 1
            pos = (pos[0] + d[0], pos[1] + d[1])
            board[pos] = steps
    return board


def solve_1(b0, b1):
    intersection_dists = [sum(map(abs, coord)) for coord in b0 if coord in b1]
    return min(intersection_dists)

def solve_2(b0, b1):
    intersection_dists = [b0[coord] + b1[coord] for coord in b0 if coord in b1]
    return min(intersection_dists)

text = open('input.txt').read()
wires = parse_input(text)
boards = [print_wire(dict(), wire) for wire in wires]
print(solve_1(*boards))
print(solve_2(*boards))
