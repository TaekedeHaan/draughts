from collections import OrderedDict

from pydraughts import BLACK_PLAYER, WHITE_PLAYER
from pydraughts import NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST
from pydraughts import ROWS, COLS, START_ROWS
from pydraughts.piece import Piece
from pydraughts.utils import init_directions, opposite_direction, diagonal
from pydraughts.move import Move
from copy import deepcopy

all_directions = init_directions(COLS, ROWS)
white_directions = {x: all_directions[x] for x in [NORTHEAST, NORTHWEST]}
black_directions = {x: all_directions[x] for x in [SOUTHEAST, SOUTHWEST]}

# dict to remember legal moves of a position for better performance
move_tables = {WHITE_PLAYER: OrderedDict(), BLACK_PLAYER: OrderedDict()}

MOVETABLE_SIZE = 200000


class Board:
    width = COLS
    height = ROWS
    start_rows = START_ROWS
    size = 2 * width * height

    def __init__(self, pieces=None):
        self.pieces = self.new_pieces() if (pieces is None) else pieces

    def copy(self):
        new_pieces = {
            player_type: player_pieces.copy()
            for player_type, player_pieces in self.pieces.items()
        }
        return Board(new_pieces)

    def key(self):
        keys = ""
        for i in range(self.size):
            if i in self.pieces[WHITE_PLAYER]:
                if self.pieces[WHITE_PLAYER][i]:
                    keys += "K"
                else:
                    keys += "P"
            elif i in self.pieces[BLACK_PLAYER]:
                if self.pieces[BLACK_PLAYER][i]:
                    keys += "k"
                else:
                    keys += "p"
            else:
                keys += "."
        return keys

    def new_pieces(self):
        pieces = {
            WHITE_PLAYER: {
                i: False
                for i in range(self.size - self.start_rows * self.width, self.size)
            },
            BLACK_PLAYER: {i: False for i in range(0, self.start_rows * self.width)},
        }
        return pieces

    def clear(self):
        """clear the pieces from the board"""
        for _, player_pieces in self.pieces.items():
            for (
                i
            ) in player_pieces.copy():  # deleting these items WHIlE looping over them
                self.remove_piece(i)

    def set_positions(
        self,
        positions_white=None,
        positions_black=None,
        kings_white=None,
        kings_black=None,
    ):
        """clear the boar and intialize the pieces at the desired locations"""
        self.clear()

        if positions_white:
            for position in positions_white:
                self.set_piece(position, WHITE_PLAYER, False)

        if kings_white:
            for position in kings_white:
                self.set_piece(position, WHITE_PLAYER, True)

        if positions_black:
            for position in positions_black:
                self.set_piece(position, BLACK_PLAYER, False)

        if kings_black:
            for position in kings_black:
                self.set_piece(position, BLACK_PLAYER, True)

    def legal_non_capture_moves(self, index):
        """
        Returns a list of legal move indexes from a set of an index on the board.
        If that index is empty, then blind_legal_moves() return an empty list.
        """
        piece_color, piece_is_king = self.get_piece(index)

        moves = []

        if piece_is_king:
            for direction, move_model in all_directions.items():
                for next_index in diagonal(index, move_model):
                    if not self.is_on_board(next_index):
                        break

                    if not self.location_is_empty(next_index):
                        break

                    moves.append(Move([index, next_index], [direction]))

        else:
            if piece_color == WHITE_PLAYER:
                directions = white_directions
            else:
                directions = black_directions

            for direction, move_model in directions.items():
                next_index = move_model[index]
                if not self.is_on_board(next_index):
                    continue

                if self.location_is_empty(next_index):
                    moves.append(Move([index, next_index], [direction]))

        return moves

    def all_legal_non_capture_moves(self, player_type):
        """All legal non-capture moves for player type"""
        all_legal_non_capture_moves = []
        for i in self.pieces[player_type]:
            legal_non_capture_moves = self.legal_non_capture_moves(i)
            all_legal_non_capture_moves.extend(legal_non_capture_moves)

        return all_legal_non_capture_moves

    def blind_single_capture_moves(self, move, previous_direction=None):
        """Blind single capture moves"""
        capture_moves = []

        index = move.locations[-1]
        if not move.directions:
            opposite_of_previous_direction = None
        else:
            opposite_of_previous_direction = opposite_direction[move.directions[-1]]

        piece_color, piece_is_king = self.get_piece(move.locations[0])
        if piece_is_king:
            for direction, move_model in all_directions.items():
                if direction == opposite_of_previous_direction:
                    continue

                capture = None
                for index_new in diagonal(index, move_model):
                    if not self.is_on_board(index_new):
                        break

                    # if the location is occupied by me, but is not the piece itself
                    if self.is_occupied_by_me(index_new, piece_color):
                        if not index_new == move.locations[0]:
                            break

                    # if occupied by opponent while
                    if (
                        self.is_occupied_by_opponent(index_new, piece_color)
                        and capture is None
                    ):
                        capture = index_new
                        continue

                    if capture in move.captures:
                        continue

                    if (
                        self.is_occupied_by_opponent(index_new, piece_color)
                        and capture is not None
                    ):
                        break

                    if (
                        self.location_is_empty(index_new)
                        or index_new == move.locations[0]
                    ) and capture is not None:
                        capture_moves.append(
                            Move([index, index_new], [direction], [capture])
                        )

        else:
            for direction, move_model in all_directions.items():
                if direction == opposite_of_previous_direction:
                    continue

                index_new = move_model[index]
                if not self.is_on_board(index_new):
                    continue

                # we cannot capture the same piece twice
                if index_new in move.captures:
                    continue

                # if opponent is on the new index square we may have a capture move, otherwise continue
                if not self.is_occupied_by_opponent(index_new, piece_color):
                    continue

                capture = index_new
                index_new = move_model[index_new]
                if not self.is_on_board(index_new):
                    continue

                # The new location should be empty, or been occupied bu the selected piece
                if self.location_is_empty(index_new) or index_new == move.locations[0]:
                    capture_moves.append(
                        Move([index, index_new], [direction], [capture])
                    )

        return capture_moves

    def has_capture_moves(self, player_type):
        """Determine whether there are capture moves for player"""
        for i in self.pieces[player_type]:
            if self.blind_single_capture_moves(Move([i])):
                return True

        return False

    def blind_capture_moves(self, moves, move, depth=0):
        if depth > 100:
            print(moves)
            raise Exception("Reached a search depth of %d on move %s" % (depth, move))

        capture_moves = self.blind_single_capture_moves(move)

        # if we can capture no more stones we store the walk
        if not capture_moves:
            if len(move.captures) > 0:
                moves.append(move)
                return

        for capture_move in capture_moves:
            new_move = move.copy()  # if len(capture_moves) > 1 else move
            new_move.append(capture_move)
            self.blind_capture_moves(moves, new_move, depth=depth + 1)

    def all_blind_capture_moves(self, player_type):
        """returns a list of all legal capture moves"""
        all_blind_capture_moves = []
        for i in self.pieces[player_type]:
            blind_capture_moves = []
            self.blind_capture_moves(blind_capture_moves, Move([i]))
            all_blind_capture_moves.extend(blind_capture_moves)

        return all_blind_capture_moves

    def all_legal_capture_moves(self, player_type):
        """selects capture moves which are equal to, the longest capture move"""
        all_blind_capture_moves = self.all_blind_capture_moves(player_type)

        if not all_blind_capture_moves:
            return []

        # the move needs to be equal to the longest move
        maximum_length = len(
            max(all_blind_capture_moves, key=lambda move: len(move.captures)).captures
        )
        return [
            move
            for move in all_blind_capture_moves
            if len(move.captures) == maximum_length
        ]

    def legal_capture_moves(self, i, player_type):
        all_legal_capture_moves = self.all_legal_capture_moves(player_type)
        if not all_legal_capture_moves:
            return []

        return [move for move in all_legal_capture_moves if move.locations[0] == i]

    def legal_moves(self, piece_xy, player_type, capturing=False):
        """get all legal moves for a piece"""
        if self.has_capture_moves(player_type) or capturing:
            legal_moves = self.legal_capture_moves(piece_xy, player_type)
        else:
            legal_moves = self.legal_non_capture_moves(piece_xy)

        return legal_moves

    def all_legal_moves(self, player_type):
        """All legal moves for player type"""
        entry = move_tables[player_type].get(self.key())
        if entry is not None:
            return entry

        all_legal_capture_moves = self.all_legal_capture_moves(player_type)

        if all_legal_capture_moves:
            all_legal_moves = all_legal_capture_moves
        else:
            all_legal_moves = self.all_legal_non_capture_moves(player_type)

        move_tables[player_type][self.key()] = all_legal_moves
        if len(move_tables[player_type]) > MOVETABLE_SIZE:
            move_tables[player_type].popitem(last=False)

        return all_legal_moves

    def is_legal_move(self, move, player):
        return move in self.all_legal_moves(player)

    def legal_move(self, i_start, i_end, player, capturing=False):
        legal_moves = self.legal_moves(i_start, player, capturing=capturing)
        for legal_move in legal_moves:
            for location in legal_move.locations[1:]:
                if i_end == location:
                    return legal_move

    def is_legal_single_move(self, i_start, i_end, player, capturing=False):
        if not self.is_on_board(i_start) or not self.is_on_board(i_end):
            return False

        legal_move = self.legal_single_move(i_start, i_end, player, capturing=capturing)
        return legal_move is not None

    def legal_single_move(self, i_start, i_end, player, capturing=False):
        legal_moves = self.legal_moves(i_start, player, capturing=capturing)
        for legal_move in legal_moves:
            sub_move = legal_move.split()[0]
            if i_end == sub_move.locations[1]:
                return sub_move

        return None

    def apply_move(self, move):
        """Apply a move"""
        for capture in move.captures:
            self.remove_piece(capture)

        # in case the piece ends up at the location is started we do not have to move it
        if move.locations[-1] != move.locations[0]:
            piece_color = self.get_piece_color(move.locations[0])
            self.pieces[piece_color][move.locations[-1]] = self.pieces[piece_color].pop(
                move.locations[0]
            )

        [self.king(location) for location in move.locations]

    def remove_piece(self, i):
        """
        Remove a piece at a certain location
        """
        if i in self.pieces[WHITE_PLAYER]:
            del self.pieces[WHITE_PLAYER][i]
        else:
            del self.pieces[BLACK_PLAYER][i]

    def set_piece(self, i, piece_color, piece_is_king):
        """
        create a piece at a certain location and make king in at king positions
        """
        self.pieces[piece_color][i] = piece_is_king

    def get_piece(self, i):
        """Get the piece at the location"""
        if i in self.pieces[WHITE_PLAYER]:
            return WHITE_PLAYER, self.pieces[WHITE_PLAYER][i]
        else:
            return BLACK_PLAYER, self.pieces[BLACK_PLAYER][i]

    def get_piece_color(self, i):
        if i in self.pieces[WHITE_PLAYER]:
            return WHITE_PLAYER
        else:
            return BLACK_PLAYER

    def get_piece_is_king(self, i):
        """Get the piece at the location"""
        if i in self.pieces[WHITE_PLAYER]:
            return self.pieces[WHITE_PLAYER][i]
        else:
            return self.pieces[BLACK_PLAYER][i]

    def location_is_empty(self, index):
        if index in self.pieces[WHITE_PLAYER]:
            return False
        return not (index in self.pieces[BLACK_PLAYER])

    def is_occupied_by_me(self, index, my_color):
        """Returns try if the location is occupied by my color"""
        return index in self.pieces[my_color]

    def is_occupied_by_opponent(self, index, my_color):
        """Returns true if the location is occupied by the opponent color"""
        return index in self.pieces[not my_color]

    def is_occupied(self, index):
        """"""
        return self.is_occupied_by_me(
            index, WHITE_PLAYER
        ) or self.is_occupied_by_opponent(index, WHITE_PLAYER)

    def is_on_board(self, i):
        """
        Checks to see if the given index lies on the board.
        If it does, then is_on_board() return True. Otherwise it returns false.
        """
        if i is None:
            return False
        return (i >= 0) and (i < self.size)

    def king(self, i):
        """
        Takes in (i), the coordinates of square to be considered for kinging.
        If it meets the criteria, then king() kings the piece in that square and kings it.
        """
        if self.location_is_empty(i):
            return

        if i < self.width:
            if self.get_piece_color(i) == WHITE_PLAYER:
                self.pieces[WHITE_PLAYER][i] = True
            return

        elif i > (self.size - self.width):
            if self.get_piece_color(i) == BLACK_PLAYER:
                self.pieces[BLACK_PLAYER][i] = True
            return

    def get_score(self, player_type, king_multiply=2):
        """calculate the score for player"""
        return sum(
            [
                1 + (king_multiply - 1) * is_king
                for i, is_king in self.pieces[player_type].items()
            ]
        )

    # testing for equivalence
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
