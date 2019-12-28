class Vec(tuple):
    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, vec):
        return Vec(*map(sum, zip(self, vec)))

    def __sub__(self, vec):
        return Vec(*map(lambda x, y: x - y, self, vec))

    def __neg__(self):
        return Vec(*map(lambda x: -x, self))

def main():
    v = Vec(1, 2, 3)
    w = Vec(4, 5, 6)
    print(v + w)
    print(v - w)

if __name__ == "__main__":
    main()
