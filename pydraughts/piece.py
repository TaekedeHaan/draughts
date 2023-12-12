import pydraughts.settings
from pydraughts import BLACK_PLAYER, WHITE_PLAYER


class Piece:
    __slots__ = ("color", "king")

    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    def crown(self):
        self.king = True
        # self.value = 2

    def copy(self):
        return Piece(self.color, self.king)

    def key(self):
        """
        Gives a key representing the piece.
        Note: probably in the future this piece class should be removed and these keys
        should be used instead
        """
        if self.king:
            if self.color == WHITE_PLAYER:
                return "K"
            else:
                return "k"
        if self.color == WHITE_PLAYER:
            return "P"
        else:
            return "p"
