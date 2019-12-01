def parse_input(filename):
    text = open(filename, 'r').read()
    return list(map(int, text.splitlines()))


def part_1(vals):
    return sum(mass//3 - 2 for mass in vals)


def part_2(vals):
    total = 0
    for mass in vals:
        while mass > 0:
            mass = mass//3 - 2
            if mass > 0:
                total += mass
    return total


if __name__ == "__main__":
    puz_input = parse_input('input.txt')

    print(part_1(puz_input))
    print(part_2(puz_input))
