import re

def get_nums(lines):
    return [list(map(int, re.findall('-?\d+', line))) for line in lines]

def solve(text):
    lines = text.splitlines()
    nums = get_nums(lines)
    for item in nums:
        print(item)

if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        solve(f.read())

