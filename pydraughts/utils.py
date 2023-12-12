from pydraughts import NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST
from pydraughts.graphics import Graphics
from multiprocessing import Value, Lock


def init_directions(board_width, board_height):
    directions = {}
    directions[NORTHEAST] = init_north_east_moves(board_width, board_height)
    directions[SOUTHEAST] = init_south_east_moves(board_width, board_height)
    directions[SOUTHWEST] = init_south_west_moves(board_width, board_height)
    directions[NORTHWEST] = init_north_west_moves(board_width, board_height)
    return directions


def init_north_east_moves(board_width, board_height):
    board_size = board_width * board_height * 2
    north_east_moves = [None] * board_size
    for i, piece in enumerate(north_east_moves):
        y = i // board_width
        row_is_even = (y % 2) == 0
        row_is_first = i < board_width
        col_is_last = ((i + 1) % 5) == 0
        if ((row_is_even) and col_is_last) or row_is_first:
            continue

        north_east_moves[i] = i - board_width + row_is_even
    return north_east_moves


def init_south_east_moves(board_width, board_height):
    board_size = board_width * board_height * 2
    north_west_moves = [None] * board_size
    for i, piece in enumerate(north_west_moves):
        y = i // board_width
        row_is_even = (y % 2) == 0
        row_is_last = y == (2 * board_height - 1)
        col_is_last = ((i + 1) % board_width) == 0
        if (row_is_even and col_is_last) or row_is_last:
            continue

        north_west_moves[i] = i + board_width + row_is_even
    return north_west_moves


def init_south_west_moves(board_width, board_height):
    board_size = board_width * board_height * 2
    north_east_moves = [None] * board_size
    for i, piece in enumerate(north_east_moves):
        y = i // board_width
        row_is_even = (y % 2) == 0
        row_is_last = y == (2 * board_height - 1)
        col_is_first = (i % board_width) == 0
        if ((not row_is_even) and col_is_first) or row_is_last:
            continue

        north_east_moves[i] = i + board_width - (not row_is_even)
    return north_east_moves


def init_north_west_moves(board_width, board_height):
    board_size = board_width * board_height * 2
    north_west_moves = [None] * board_size
    for i, piece in enumerate(north_west_moves):
        y = i // board_width
        row_is_even = (y % 2) == 0
        row_is_first = i < board_width
        col_is_first = (i % board_width) == 0
        if ((not row_is_even) and col_is_first) or row_is_first:
            continue

        north_west_moves[i] = i - (board_width + (not row_is_even))
    return north_west_moves


opposite_direction = {
    NORTHEAST: SOUTHWEST,
    SOUTHWEST: NORTHEAST,
    NORTHWEST: SOUTHEAST,
    SOUTHEAST: NORTHWEST,
    None: None,
}


def diagonal(index, direction):
    """
    generator for squares from i in direction d
    """
    next_index = index
    stop = direction[next_index] is None
    while not stop:
        next_index = direction[next_index]
        stop = direction[next_index] is None
        yield next_index


def show(board):
    graphics = Graphics()
    graphics.setup_window()
    graphics.update_display(board)

    # TODO: continue is we close window
    while True:
        pass


class MultiThreadCounter(object):
    def __init__(self, manager, val=0):
        self.val = manager.Value("i", val)
        self.lock = manager.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value


class Counter(object):
    def __init__(self, val=0):
        self.val = val

    def increment(self):
        self.val += 1

    def value(self):
        return self.val


# class Counter(object):
#     def __init__(self, manager, initval=0):
#         self.val = manager.Value('i', initval)
#         self.lock = manager.Lock()
#
#     def increment(self):
#         with self.lock:
#             self.val.value += 1
#
#     def value(self):
#         with self.lock:
#             return self.val.value
