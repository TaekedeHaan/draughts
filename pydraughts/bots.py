import random
import time


class RandomWalker(object):
    def __init__(self, name=None):
        if name is None:
            name = "random_name"

        self.name = name
        self.player_type = None
        self.move = None

    def take_action(self, board, graphics, capturing=False):
        all_legal_moves = board.all_legal_moves(self.player_type)
        i_move = random.randrange(len(all_legal_moves))
        self.move = all_legal_moves[i_move]

    def reset(self):
        self.move = None
