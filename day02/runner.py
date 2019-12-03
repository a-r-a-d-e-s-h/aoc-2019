class Op:
    retval = 0
    def step(self):
        rip = self.computer.instruction_pointer
        args = self.computer.memory.memory[rip + 1: rip + self.size]
        self.func(*args)
        self.computer.instruction_pointer += self.size
        return self.retval

    def get(self, addr):
        return self.computer.get(addr)

    def set(self, addr, val):
        self.computer.set(addr, val)

    def __call__(self):
        return self.step()

class Add(Op):
    size = 4
    def func(self, x0, x1, y):
        self.set(y, self.get(x0) + self.get(x1))

class Mul(Op):
    size = 4
    def func(self, x0, x1, y):
        self.set(y, self.get(x0) * self.get(x1))

class Halt(Op):
    retval = 1
    size = 1

    def func(self):
        pass

class Memory:
    def load_from_file(self, fn):
        self.initial_memory = tuple(map(int, open(fn).read().split(',')))
        self.memory = list(self.initial_memory)

    def reset(self):
        self.memory = list(self.initial_memory)

    def get(self, addr):
        return self.memory[addr]

    def set(self, addr, val):
        self.memory[addr] = val

class Computer:
    ops = {
        1: Add(),
        2: Mul(),
        99: Halt()
    }
    def __init__(self):
        self.memory = Memory()
        self.instruction_pointer = 0
        for key, op in self.ops.items():
            op.computer = self

    def load(self, filename):
        self.memory.load_from_file(filename)

    def reset(self):
        self.memory.reset()

    def run(self):
        self.instruction_pointer = 0
        while 1:
            rip = self.instruction_pointer
            opcode = self.get(rip)
            if self.ops[opcode]():
                return 0

    def get(self, addr):
        return self.memory.get(addr)

    def set(self, addr, val):
        self.memory.set(addr, val)

computer = Computer()
computer.load("input.txt")
computer.set(1, 12)
computer.set(2, 2)
computer.run()
print(computer.get(0))

noun = 0
while 1:
    for verb in range(100):
        computer.reset()
        computer.set(1, noun)
        computer.set(2, verb)
        computer.run()
        if computer.get(0) == 19690720:
            print(100*noun + verb)
            break
    else:
        noun += 1
        continue
    break
