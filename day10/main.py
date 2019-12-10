from itertools import cycle

filename = "input.txt"


def load_map(filename):
    return open(filename).read().splitlines()


class Tile:
    EMPTY = '.'
    ASTEROID = '#'


def gcd(x, y):
    x = abs(x)
    y = abs(y)
    if x <= y:
        if x == 0:
            return y
        return gcd(x, y % x)
    else:
        return gcd(y, x)


def reduce_pair(x, y):
    d = gcd(x, y)
    return x//d, y//d


def order_directions(dirs):
    row_pos = []
    row_neg = []
    row_0_col_pos = []
    row_0_col_neg = []

    for vec in dirs:
        col, row = vec
        if row > 0:
            row_pos.append(vec)
        elif row < 0:
            row_neg.append(vec)
        else:  # row == 0
            if col > 0:
                row_0_col_pos.append(vec)
            else:
                row_0_col_neg.append(vec)
    row_pos.sort(key=lambda x: x[0]/x[1])
    row_neg.sort(key=lambda x: x[0]/x[1])

    ret = (row_0_col_neg + row_pos + row_0_col_pos + row_neg)
    ret.reverse()
    return ret


def get_visible_directions(layout, pos):
    start_col, start_row = pos
    tot_rows = len(layout)
    tot_cols = len(layout[0])
    asteroids = []
    for row_i, row in enumerate(layout):
        for col_i, tile in enumerate(row):
            if tile == Tile.ASTEROID:
                asteroids.append((col_i, row_i))

    visible_directions = set()
    for (col_i, row_i) in asteroids:
        rel_col = col_i - start_col
        rel_row = row_i - start_row
        if rel_col == rel_row == 0:
            continue
        rel_col, rel_row = reduce_pair(rel_col, rel_row)
        visible_directions.add(reduce_pair(rel_col, rel_row))

    return visible_directions


def count_visible(layout, pos):
    return len(get_visible_directions(layout, pos))


def solve_1(layout):
    results = []
    for row_i, row in enumerate(layout):
        for col_i, col in enumerate(row):
            if col == Tile.ASTEROID:
                results.append((
                    count_visible(layout, (col_i, row_i)),
                    (col_i, row_i)
                ))

    return max(results, key=lambda x: x[0])


def solve_2(layout, pos):
    dirs = get_visible_directions(layout, pos)
    start_dir = (0, -1)
    if start_dir not in dirs:
        dirs.add(start_dir)
    ordered_dirs = order_directions(dirs)
    start_index = ordered_dirs.index(start_dir)
    ordered_dirs = ordered_dirs[start_index:] + ordered_dirs[:start_index]

    asteroid_locations = []

    for row_i, row in enumerate(layout):
        for col_i, col in enumerate(row):
            if col == Tile.ASTEROID:
                asteroid_locations.append((col_i, row_i))
    asteroid_locations.remove(pos)

    vaporized_count = 0

    pos_col, pos_row = pos

    for direction in cycle(ordered_dirs):
        if not asteroid_locations:
            break
        dir_col, dir_row = direction
        candidates = []
        for ast_col, ast_row in asteroid_locations:
            rel_row = ast_row - pos_row
            rel_col = ast_col - pos_col
            if rel_col*dir_row == rel_row*dir_col:
                if rel_col == 0:
                    if rel_row/dir_row > 0:
                        candidates.append((rel_col, rel_row))
                else:
                    if rel_col/dir_col > 0:
                        candidates.append((rel_col, rel_row))

        if candidates:
            vaporize = min(candidates, key=lambda x: (abs(x[0]), abs(x[1])))
            ast = pos_col + vaporize[0], pos_row + vaporize[1]
            asteroid_locations.remove(ast)
            vaporized_count += 1

            if vaporized_count == 200:
                return ast


def main():
    layout = load_map(filename)
    max_num, pos = solve_1(layout)
    print(max_num)
    res = solve_2(layout, pos)
    print(100*res[0] + res[1])


main()
