import pygame
import sys
import time
import datetime
from pydraughts.turn import Turn

from pydraughts import WHITE_PLAYER, BLACK_PLAYER
from pydraughts.graphics import Graphics
from pydraughts.board import Board


class Game:
    """
    The main game control.
    """

    def __init__(
        self,
        player1=None,
        player2=None,
        board=None,
        time_limit=20.0,
        do_multi_thread=True,
    ):
        self.graphics = Graphics()
        self.board = Board() if (board is None) else board
        self.quit = False
        self.turn = WHITE_PLAYER
        self.moves = []
        self.do_multi_thread = do_multi_thread

        if player1 is None:
            raise Exception("Please select a pydraughts agent for player1")

        if player2 is None:
            raise Exception("Please select a pydraughts agent for player2")

        player1.player_type = WHITE_PLAYER
        player2.player_type = BLACK_PLAYER
        self.player = {WHITE_PLAYER: player1, BLACK_PLAYER: player2}

        self.next_turn = {WHITE_PLAYER: BLACK_PLAYER, BLACK_PLAYER: WHITE_PLAYER}

        self.action = {
            WHITE_PLAYER: Turn(player1, self.do_multi_thread),
            BLACK_PLAYER: Turn(player2, self.do_multi_thread),
        }

        self.time = {
            WHITE_PLAYER: time_limit * 60,  # [s]
            BLACK_PLAYER: time_limit * 60,  # [s]
        }
        self.time_current = self.time.copy()

    def play(self):
        """ "This executes the game and controls its flow."""
        self.update()
        self.setup()
        while not self.quit:
            self.take_turn()

        self.terminate_game()

    def setup(self):
        """Draws the window and board at the beginning of the game"""
        self.graphics.setup_window()

    def take_turn(self):
        action = self.action[self.turn]
        action.take(self.board, self.graphics, self.turn)
        self.time_current[self.turn] = self.time[self.turn] - action.duration

        if action.move is not None:
            move = action.move

            self.time[self.turn] -= action.duration
            self.board.apply_move(move)
            self.moves.append(move)
            self.end_turn()

            action.clean()

        self.update()

    def end_turn(self):
        """
        End the turn. Switches the current player.
        end_turn() also checks for and game and resets a lot of class attributes.
        """
        self.turn = self.next_turn[self.turn]

        if self.check_for_endgame():
            if self.turn == WHITE_PLAYER:
                print("BLACK_PLAYER WINS!")
                self.graphics.draw_message("BLACK_PLAYER WINS!")
            else:
                print("WHITE_PLAYER WINS!")
                self.graphics.draw_message("WHITE_PLAYER WINS!")

            self.quit = True
            self.terminate_game()

    def update(self):
        """Calls on the graphics class to update the game display."""
        self.graphics.move_history = self.moves
        self.graphics.time = self.time_current
        self.graphics.update_display(self.board)

    def terminate_game(self):
        """Quits the program and ends the game."""
        pygame.quit()
        sys.exit()

    def check_for_endgame(self):
        """
        Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
        """
        for i in self.board.pieces[self.turn]:
            if self.board.legal_moves(i, self.turn):
                return False

        return True
