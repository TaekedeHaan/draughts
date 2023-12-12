import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# from pygame.piece import Piece
from pydraughts.move import Move
from pydraughts.graphics import board_coords


class HumanPlayer(object):
    def __init__(self, name=None):
        if name is None:
            name = "random_name"

        self.name = name
        self.player_type = None
        self.selected_piece = None
        self.move = None
        self.capturing = False
        self.graphics = None

    def take_action(self, board, graphics, capturing=False):
        """
        The event loop. This is where events are triggered
        (like a mouse click) and then effect the game state.
        """
        self.graphics = graphics
        # self.selected_piece = None
        while True:
            mouse_pos = tuple(map(int, pygame.mouse.get_pos()))
            mouse_pos = board_coords(mouse_pos)

            if (self.selected_piece is None) and (mouse_pos is not None):
                if board.is_occupied(mouse_pos):
                    # self.selected_piece = mouse_pos
                    if board.is_occupied_by_me(mouse_pos, self.player_type):
                        self.highlight_moves(board, graphics, mouse_pos)

            elif self.selected_piece is not None:
                self.highlight_moves(board, graphics, self.selected_piece)

            for event in pygame.event.get():
                if event.type == QUIT:
                    print("Human player received quit event")
                    return

                if event.type == MOUSEBUTTONDOWN:
                    # click outside of the squares
                    if mouse_pos is None:
                        continue

                    # upon selecting the same piece, deselect
                    if self.selected_piece == mouse_pos and not self.capturing:
                        self.selected_piece = None
                        continue

                    # upon selecting another piece, update
                    if (
                        board.is_occupied_by_me(mouse_pos, self.player_type)
                        and not self.capturing
                    ):
                        self.selected_piece = mouse_pos
                        continue

                    # upon selecting an empty square, determine move
                    if self.selected_piece is not None:
                        if board.is_legal_single_move(
                            self.selected_piece, mouse_pos, self.player_type
                        ):
                            sub_move = board.legal_single_move(
                                self.selected_piece, mouse_pos, self.player_type
                            )

                            # if not a capture move we are done
                            if not sub_move.is_capture_move():
                                self.move = sub_move
                                return

                            # otherwise check if there is a next move available
                            board.apply_move(sub_move)
                            self.selected_piece = mouse_pos

                            capture_moves = board.legal_capture_moves(
                                self.selected_piece, self.player_type
                            )

                            if self.move is None:
                                self.move = sub_move
                            else:
                                self.move.append(sub_move)

                            if len(capture_moves) == 0:
                                return

                            graphics.update_display(
                                board
                            )  # TODO: what to do with this?
                            self.capturing = True

    def highlight_moves(self, board, graphics, location):
        legal_moves = board.legal_moves(
            location, self.player_type, capturing=self.capturing
        )
        graphics.legal_moves = [
            location for move in legal_moves for location in move.locations
        ]
        graphics.selected_piece = location

    def reset(self):
        self.graphics.legal_moves = None
        self.graphics.selected_piece = None
        self.selected_piece = None
        self.move = None
        self.capturing = False
