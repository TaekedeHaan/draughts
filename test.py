import unittest
from pydraughts.board import Board
from pydraughts.move import Move
from pydraughts.graphics import Graphics
from pydraughts import WHITE_PLAYER, BLACK_PLAYER
from pydraughts import NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST
from pydraughts.utils import show


class TestBoardMethods(unittest.TestCase):
    def test_clear_board(self):
        board = Board()
        board.clear()
        self.assertEqual(board.pieces[WHITE_PLAYER], {})
        self.assertEqual(board.pieces[BLACK_PLAYER], {})


class TestLegalCaptureMovesMethods(unittest.TestCase):
    def test_single_capture(self):
        board = Board()
        board.set_positions(positions_white=[7], positions_black=[12])
        moves_result_white = [Move([7, 18], [SOUTHEAST], [12])]
        moves_result_black = [Move([12, 1], [NORTHWEST], [7])]
        self.assertEqual(moves_result_white, board.legal_moves(7, WHITE_PLAYER))
        self.assertEqual(moves_result_black, board.legal_moves(12, BLACK_PLAYER))

    def test_circular_capture(self):
        """Do not want to get stuck in recursion"""
        board = Board()
        board.set_positions(positions_white=[7], positions_black=[12, 22, 21, 11])
        move_result = [
            Move(
                [7, 18, 27, 16, 7],
                [SOUTHEAST, SOUTHWEST, NORTHWEST, NORTHEAST],
                [12, 22, 21, 11],
            ),
            Move(
                [7, 16, 27, 18, 7],
                [SOUTHWEST, SOUTHEAST, NORTHEAST, NORTHWEST],
                [11, 21, 22, 12],
            ),
        ]
        self.assertEqual(move_result, board.legal_moves(7, WHITE_PLAYER))

    def test_circular_capture_2(self):
        """more complex scenario than the previous test"""
        board = Board()
        board.set_positions(
            positions_white=[6], positions_black=[10, 20, 11, 21, 12, 22, 13, 23]
        )
        move_result = [
            Move(
                [6, 17, 8, 19, 28, 17, 26, 15, 6],
                [
                    SOUTHEAST,
                    NORTHEAST,
                    SOUTHEAST,
                    SOUTHWEST,
                    NORTHWEST,
                    SOUTHWEST,
                    NORTHWEST,
                    NORTHEAST,
                ],
                [11, 12, 13, 23, 22, 21, 20, 10],
            ),
            Move(
                [6, 17, 28, 19, 8, 17, 26, 15, 6],
                [
                    SOUTHEAST,
                    SOUTHEAST,
                    NORTHEAST,
                    NORTHWEST,
                    SOUTHWEST,
                    SOUTHWEST,
                    NORTHWEST,
                    NORTHEAST,
                ],
                [11, 22, 23, 13, 12, 21, 20, 10],
            ),
            Move(
                [6, 15, 26, 17, 8, 19, 28, 17, 6],
                [
                    SOUTHWEST,
                    SOUTHEAST,
                    NORTHEAST,
                    NORTHEAST,
                    SOUTHEAST,
                    SOUTHWEST,
                    NORTHWEST,
                    NORTHWEST,
                ],
                [10, 20, 21, 12, 13, 23, 22, 11],
            ),
            Move(
                [6, 15, 26, 17, 28, 19, 8, 17, 6],
                [
                    SOUTHWEST,
                    SOUTHEAST,
                    NORTHEAST,
                    SOUTHEAST,
                    NORTHEAST,
                    NORTHWEST,
                    SOUTHWEST,
                    NORTHWEST,
                ],
                [10, 20, 21, 22, 23, 13, 12, 11],
            ),
        ]
        self.assertEqual(move_result, board.legal_moves(6, WHITE_PLAYER))

    def test_longest_capture(self):
        board = Board()
        board.set_positions(
            positions_white=[6], positions_black=[10, 11, 21, 22, 33, 43]
        )
        move_result = [
            Move(
                [6, 17, 28, 39, 48],
                [SOUTHEAST, SOUTHEAST, SOUTHEAST, SOUTHWEST],
                [11, 22, 33, 43],
            )
        ]
        self.assertEqual(move_result, board.legal_moves(6, WHITE_PLAYER))


class TestKinging(unittest.TestCase):
    """unit tests for kinging"""

    def test_basic_kinging_white(self):
        board = Board()
        board.set_positions(positions_white=[6])
        self.assertEqual(board.get_piece_is_king(6), False)
        board.apply_move(Move([6, 0], [NORTHWEST]))
        self.assertEqual(board.get_piece_is_king(0), True)

    def test_basic_not_kinging_white(self):
        board = Board()
        board.set_positions(positions_white=[43])
        self.assertEqual(board.get_piece_is_king(43), False)
        board.apply_move(Move([43, 49], [SOUTHEAST]))
        self.assertEqual(board.get_piece_is_king(49), False)

    def test_basic_kinging_black(self):
        board = Board()
        board.set_positions(positions_black=[42])
        self.assertEqual(board.get_piece_is_king(42), False)
        board.apply_move(Move([42, 48], [SOUTHEAST]))
        self.assertEqual(board.get_piece_is_king(48), True)

    def test_basic_not_kinging_white(self):
        board = Board()
        board.set_positions(positions_black=[8])
        self.assertEqual(board.get_piece(8)[1], False)
        board.apply_move(Move([8, 2], [NORTHEAST]))
        self.assertEqual(board.get_piece(2)[1], False)


class TestKingLegalCaptureMovesMethods(unittest.TestCase):
    """Tests for the legal capture moves of kings"""

    def test_basic_capture(self):
        board = Board()
        board.set_positions(kings_white=[7], positions_black=[29])
        moves_result_white = [Move([7, 34], [SOUTHEAST], [29])]
        self.assertEqual(moves_result_white, board.legal_moves(7, WHITE_PLAYER))

    def test_circular_capture(self):
        """Do not want to get stuck in recursion"""
        board = Board()
        board.set_positions(kings_white=[7], positions_black=[18, 38, 36, 16])
        moves = board.legal_moves(7, WHITE_PLAYER)

        move_result = [
            Move(
                [7, 29, 47, 25, 11],
                [SOUTHEAST, SOUTHWEST, NORTHWEST, NORTHEAST],
                [18, 38, 36, 16],
            ),
            Move(
                [7, 29, 47, 25, 7],
                [SOUTHEAST, SOUTHWEST, NORTHWEST, NORTHEAST],
                [18, 38, 36, 16],
            ),
            Move(
                [7, 29, 47, 25, 2],
                [SOUTHEAST, SOUTHWEST, NORTHWEST, NORTHEAST],
                [18, 38, 36, 16],
            ),
            Move(
                [7, 25, 47, 29, 12],
                [SOUTHWEST, SOUTHEAST, NORTHEAST, NORTHWEST],
                [16, 36, 38, 18],
            ),
            Move(
                [7, 25, 47, 29, 7],
                [SOUTHWEST, SOUTHEAST, NORTHEAST, NORTHWEST],
                [16, 36, 38, 18],
            ),
            Move(
                [7, 25, 47, 29, 1],
                [SOUTHWEST, SOUTHEAST, NORTHEAST, NORTHWEST],
                [16, 36, 38, 18],
            ),
        ]
        self.assertEqual(move_result, moves)


if __name__ == "__main__":
    unittest.main()
