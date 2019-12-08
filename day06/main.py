from collections import defaultdict

filename = 'input.txt'

def solve_1(relations):
    counts = {}

    def count_parents(planet):
        if planet in counts:
            return counts[planet]
        else:
            if planet in relations:
                return 1 + count_parents(relations[planet])
            else:
                return 0

    for planet in relations.keys():
        counts[planet] = count_parents(planet)

    return sum(counts.values())


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
    data = [line.strip().split(')') for line in open(filename)]
    relations = {}
    for a, b in data:
        relations[b] = a
    print(solve_1(relations))
    print(solve_2(relations))

main()
