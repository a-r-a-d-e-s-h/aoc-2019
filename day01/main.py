def parse_input(filename):
    return map(int, open(filename))


def part_1(vals):
    return sum(mass//3 - 2 for mass in vals)


def part_2(vals):
    total = 0
    for mass in vals:
        while mass > 0:
            mass = mass//3 - 2
            total += max(0, mass)
    return total


puz_input = parse_input('input.txt')

print(part_1(puz_input))
print(part_2(puz_input))
