from collections import deque
import bisect

class OrderedList:
    def __init__(self, initial):
        self.items = deque(sorted(initial))

if __name__ == "__main__":
    x = OrderedList([1, 100])
    print(x.items[0])
