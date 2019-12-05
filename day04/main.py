from collections import defaultdict

def has_repeat(nums):
    length = len(nums) - 1
    for i in range(length):
        if nums[i] == nums[i+1]:
            return True
    return False

def condition_2(nums):
    groups = defaultdict(int)
    for digit in nums:
        groups[digit] += 1
    return 2 in groups.values()

def count_between(lower, upper, init):
    total = 0
    if len(init) == len(lower):
        if lower <= init <= upper:
            if condition_2(init):
                return 1
        return 0

    if init:
        start = init[-1]
    else:
        start = lower[0]
        end = upper[0]
    for i in range(int(start), 10):
        total += count_between(lower, upper, init + str(i))
    return total



def main():
    f = open('input.txt')
    code = f.read()
    lower, upper = code.split('-')
    print(count_between(lower, upper, init=''))
main()
