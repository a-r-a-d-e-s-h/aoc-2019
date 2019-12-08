from collections import Counter


class Colour:
    BLACK = '0'
    WHITE = '1'
    TRANSPARENT = '2'

    display_map = {
        BLACK: ' ',
        WHITE: '#',
        TRANSPARENT: '~'
    }

    @classmethod
    def display(cls, code):
        return cls.display_map[code]


def solve_1(layers):
    min_layer = min(layers, key=lambda layer: Counter(layer)['0'])
    counter = Counter(min_layer)
    return counter['1']*counter['2']


def solve_2(layers):
    image = [Colour.TRANSPARENT] * len(layers[0])
    for layer in layers:
        for i, pixel in enumerate(layer):
            if image[i] == Colour.TRANSPARENT:
                image[i] = pixel
    return image


def draw_image(image, width, height):
    image = list(map(Colour.display, image))
    area = len(image)
    lines = (''.join(image[i:i+width]) for i in range(0, area, width))
    return '\n'.join(lines)


text = open('input.txt').read()
layers = []
width = 25
height = 6
area = width*height
for i in range(0, len(text), area):
    layers.append(text[i:i+area])

print(solve_1(layers))
print(draw_image(solve_2(layers), width, height))
