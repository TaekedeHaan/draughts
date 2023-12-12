import pygame
from threading import Thread


class Turn(object):
    """
    This class interacts with the player to obtain a move, this is done in a separate thread, such that the main game
    will not be blocked.
    """

    def __init__(self, player, in_separate_thread=True):
        self.player = player
        self.in_separate_thread = in_separate_thread

        self.start_time = None
        self.duration = None
        self.thread = None
        self.move = None

    def take(self, board, graphics, player_type):
        """"""
        if self.thread is None:
            self.start(board, graphics)

        current_time = pygame.time.get_ticks()  # [ms]
        self.duration = (current_time - self.start_time) / 1000

        if not self.is_busy():
            self.end(board, player_type)

    def start(self, board, graphics):
        """Start a player turn on a separate thread"""
        self.start_time = pygame.time.get_ticks()  # [ms]

        if self.in_separate_thread:
            self.thread = Thread(
                target=self.player.take_action, args=(board.copy(), graphics)
            )
            self.thread.start()
        else:
            self.thread = self.player.take_action(board.copy(), graphics)

    def end(self, board, player_type):
        move = self.player.move

        if move is None:
            return

        # only legal moves are accepted
        if not board.is_legal_move(move, player_type):
            print("Player suggested in illegal move %s" % move)
            print("Legal moves are: ")
            [
                print(" - %s" % legal_move)
                for legal_move in board.all_legal_moves(player_type)
            ]
            return

        self.move = move
        print("duration: %f" % self.duration)

    def clean(self):
        self.player.reset()
        self.start_time = None
        self.duration = None
        self.thread = None
        self.move = None

    def is_busy(self):
        if not self.in_separate_thread:
            return False

        if self.thread is None:
            print("thread is still empty!")
            return False

        return self.thread.is_alive()
