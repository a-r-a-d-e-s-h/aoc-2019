def parse_input(filename):
    return tuple(map(int, open(filename).read().split(',')))

def runner(data, noun, verb):
    data = list(data)
    data[1] = noun
    data[2] = verb
    position = 0
    while 1:
        op_code, x0, x1, y = data[position:position+4]
        if op_code == 1:
            data[y] = data[x0] + data[x1]
        elif op_code == 2:
            data[y] = data[x0] * data[x1]
        else:
            return data[0]
        position += 4
    return data[0]

def solve_1(data):
    return runner(data, 12, 2)

def solve_2(data):
    noun = 0
    while 1:
        for verb in range(100): # Assume verb can be at most 2 digits
            if runner(data, noun, verb) == 19690720:
                return(100*noun + verb)
        else:
            noun += 1
        
data = parse_input('input.txt')
print(solve_1(data))
print(solve_2(data))
