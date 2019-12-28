from collections import Counter


def non_decreasing_iter(val, end):
    while val <= end:
        digits = list(str(val))
        last_digit = '0'
        for i, digit in enumerate(digits):
            digits[i] = max(last_digit, digit)
            last_digit = digits[i]
        val = ''.join(digits)
        yield val
        val = str(int(val) + 1)


f = open('input.txt')
code = f.read()
lower, upper = code.split('-')

p1 = p2 = 0
everything = 0
for val in non_decreasing_iter(lower, upper):
    everything += 1
    counter_vals = Counter(val).values()
    p1 += (max(counter_vals) >= 2)
    p2 += 2 in counter_vals


print(p1)
print(p2)
