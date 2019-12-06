from collections import defaultdict

filename = 'input.txt'

def parse_data(text):
    lines = text.splitlines()
    return [item.split(')') for item in lines]

def solve_1(relations):
    done = {}
    remaining = set(relations.keys())

    def recursive_calculate(item):
        if item in relations:
            item_orbits = relations[item]
            recursive_calculate(item_orbits)
            done[item] = 1 + done[item_orbits]
            if item in remaining:
                remaining.remove(item)
        else:
            done[item] = 0

    while remaining:
        recursive_calculate(remaining.pop())

    return sum(done.values())


def min_steps(relations, start, end):
    valid_steps = defaultdict(set)
    for a, b in relations.items():
        valid_steps[a].add(b)
        valid_steps[b].add(a)

    start = relations[start]
    end = relations[end]

    to_do = {start}
    shortest = {start: 0}

    while to_do:
        item = to_do.pop()
        for nbour in valid_steps[item]:
            if nbour not in shortest:
                shortest[nbour] = shortest[item] + 1
                to_do.add(nbour)

    return shortest[end]


def solve_2(data):
    return min_steps(data, "YOU", "SAN")


def main():
    f = open(filename)
    data = parse_data(f.read())
    relations = {}
    for a, b in data:
        relations[b] = a
    print(solve_1(relations))
    print(solve_2(relations))

main()
