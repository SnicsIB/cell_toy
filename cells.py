from collections import defaultdict
from bearlibterminal import terminal
import numpy as np


class Rulebook:
    """Simple rulebook for cellular automata"""

    def __init__(self, rules_dict=None):
        if rules_dict is None:
            rules_dict = defaultdict(
                lambda: defaultdict(
                    lambda: (-1, -1, 0.0)
                )
            )
        self.rules = rules_dict

    def new_rule(self, a, b, result, priority=0, probability=1.0):
        """New rule for a game. Returns result (new state) for cell a"""
        self.rules[a][b] = (result, priority, probability)

    def __call__(self, cell, neighbours):
        """
        Returns result for cell. The highest priority rule (if equal priority exist than first) will be applied.
        No change -- priority 0.
        """
        candidate = (cell, 0)
        for neighbour in neighbours:
            if self.rules[cell][neighbour][1] >= candidate[1]:
                if np.random.rand() < self.rules[cell][neighbour][2]:
                    candidate = self.rules[cell][neighbour]
        return candidate[0]


def print_state(matrix, colors):
    for index, cell in np.ndenumerate(matrix):
        terminal.put_ext(index[1] + 1, index[0] + 1, 0, 0, 0x2588, colors[int(cell)])


def get_adj_cells(_i, _j, len_i, len_j):
    return tuple(filter(
        lambda k: -1 < k[0] < len_i and -1 < k[1] < len_j,
        [
            (_i - 1, _j),
            (_i, _j - 1),
            (_i, _j + 1),
            (_i + 1, _j),
        ]))


def calculate_step(matrix, rulebook):
    new = np.copy(matrix)
    for index, cell in np.ndenumerate(matrix):
        neighbours = get_adj_cells(*index, *matrix.shape)
        new[index] = rulebook(
            cell,
            matrix[
                [k[0] for k in neighbours],
                [k[1] for k in neighbours]
            ]
        )
    return new


# example
# params
width = 20
height = 20
# define rules
rules = Rulebook()
# >2 | 1 => 1 | 1 (Excitement)
rules.new_rule(0, 1, 1, probability=1)
rules.new_rule(3, 1, 1, probability=0.1)
rules.new_rule(4, 1, 1, probability=0.2)
rules.new_rule(5, 1, 1, probability=0.3)
rules.new_rule(6, 1, 1, probability=0.4)
# 1 | ANY => 2 | ANY (Absolute refractory period)
rules.new_rule(1, 3, 2, probability=1)
rules.new_rule(1, 2, 2, probability=1)
rules.new_rule(1, 1, 2, probability=1)
rules.new_rule(1, 0, 2, probability=1)
# Relative refractory period
for i in range(2, 7):
    for j in range(7):
        rules.new_rule(i, j, (i + 1) % 7, probability=0.5)
print(rules.rules)

w_matrix = np.random.random_integers(0, 8, size=(height, width))

# colors for different cell types.
colors_list = [
    [terminal.color_from_argb(200, 5, 5, 5)] * 4,
    [terminal.color_from_argb(200, 225, 0, 255)] * 4,
    [terminal.color_from_argb(100, 200, 0, 255)] * 4,
    [terminal.color_from_argb(50, 150, 0, 225)] * 4,
    [terminal.color_from_argb(25, 100, 0, 150)] * 4,
    [terminal.color_from_argb(12, 75, 0, 120)] * 4,
    [terminal.color_from_argb(6, 35, 0, 60)] * 4,
    [terminal.color_from_argb(3, 15, 0, 30)] * 4,
    [terminal.color_from_argb(100, 255, 255, 30)] * 4,
]

# init terminal
terminal.open()
terminal.set("""
window: size={}x{}, cellsize=14x14, title='Cells';
font: unifont-12.1.02.ttf, size=12;
input: precise-mouse = false,
       mouse-cursor = true,
       filter=[keyboard, mouse+];
""".format(width + 2, height + 2))
print_state(w_matrix, colors_list)
terminal.refresh()
w_matrix = calculate_step(w_matrix, rules)

# main cycle
response = terminal.TK_SPACE
running = True
while response != terminal.TK_CLOSE:
    if response == terminal.TK_SPACE:
        running = not running
    if running or response == terminal.TK_F:
        print_state(w_matrix, colors_list)
        terminal.refresh()
        w_matrix = calculate_step(w_matrix, rules)
    # input
    if response == terminal.TK_MOUSE_LEFT:
        y = terminal.state(terminal.TK_MOUSE_Y)
        x = terminal.state(terminal.TK_MOUSE_X)
        w_matrix[y - 1][x - 1] = 1
        print_state(w_matrix, colors_list)
        terminal.refresh()
    response = -1
    if terminal.has_input():
        response = terminal.read()

terminal.close()
