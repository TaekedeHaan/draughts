from pydraughts import HIGH, HIGH2, GOLD, WHITE_PLAYER, BLACK_PLAYER
from pydraughts import (
    COLOR_LIGHT_SQUARE,
    COLOR_DARK_SQUARE,
    COLOR_BLACK_PLAYER,
    COLOR_WHITE_PLAYER,
)
from pydraughts import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SQUARE_WIDTH,
    SQUARE_HEIGHT,
    ROWS,
    COLS,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)
from pydraughts import (
    HEADER_LEFT,
    HEADER_RIGHT,
    HEADER_TOP,
    HEADER_BOTTOM,
    MARGIN,
    LINE_HEIGHT,
)
from pydraughts import BOARD_IMAGE
import os
import pygame


def list_to_matrix_coords(i):
    """1D to 2D board coordinates"""
    y = i // COLS
    x = 2 * (i % COLS) + ((y % 2) == 0)
    return x, y


def matrix_to_list_coords(xy):
    """2D to 1D board coordinates"""
    x = xy[0]
    y = xy[1]
    if not (x + y) % 2:
        return None

    xi = (x - ((y % 2) == 0)) // 2
    yi = y * COLS
    return xi + yi


def time_to_str(time):
    """Converts time in seconds to a human readbale string"""
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def board_coords(pixel_xy):
    """
    Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
    """
    x = pixel_xy[0] - HEADER_LEFT
    y = pixel_xy[1] - HEADER_TOP
    if x < 0 or x > BOARD_WIDTH:
        return None
    if y < 0 or y > BOARD_HEIGHT:
        return None

    xy = (x // SQUARE_WIDTH, y // SQUARE_HEIGHT)
    return matrix_to_list_coords(xy)


def pixel_coords(board_coords, do_center=True):
    """
    Takes in a of board coordinate and returns the pixel coordinates of the center of the square at that location.
    """
    return (
        board_coords[0] * SQUARE_WIDTH + do_center * (SQUARE_WIDTH // 2) + HEADER_LEFT,
        board_coords[1] * SQUARE_HEIGHT + do_center * (SQUARE_HEIGHT // 2) + HEADER_TOP,
    )


class Graphics:
    caption = "pypydraughts"
    icon_file = os.path.join("resources", "checkers.png")

    def __init__(self):
        self.fps = 60
        self.clock = pygame.time.Clock()

        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        # we need to load icon before set_mode
        # self.setup_window()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.screen.fill(COLOR_BLACK_PLAYER)

        # this should not be here!
        self.move_history = None
        self.time = None
        self.selected_piece = None
        self.legal_moves = None

        if BOARD_IMAGE is not None:
            self.board_image = pygame.image.load(BOARD_IMAGE)
        else:
            self.board_image = None

        # TODO: get from board.size
        self.square_width = SQUARE_WIDTH
        self.square_height = SQUARE_HEIGHT
        self.piece_size = self.square_width // 2.2

        pygame.init()
        self.font = pygame.font.Font("freesansbold.ttf", 18)

        text_surface_obj = self.font.render(
            "white", True, COLOR_LIGHT_SQUARE, COLOR_BLACK_PLAYER
        )
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.top = HEADER_TOP + MARGIN
        text_rect_obj.left = MARGIN
        self.screen.blit(text_surface_obj, text_rect_obj)

        text_surface_obj = self.font.render(
            "black", True, COLOR_LIGHT_SQUARE, COLOR_BLACK_PLAYER
        )
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.top = HEADER_TOP + MARGIN
        text_rect_obj.left = HEADER_LEFT + BOARD_WIDTH + MARGIN
        self.screen.blit(text_surface_obj, text_rect_obj)

    def setup_window(self):
        """
        This initializes the window and sets the caption at the top.
        """
        pygame.display.set_caption(self.caption)
        if not os.path.isfile(self.icon_file):
            print("Failed to load icon: file does not exist!")

        icon = pygame.image.load(self.icon_file)
        pygame.display.set_icon(icon)

    def update_display(self, board):
        """
        This updates the current display.
        """
        # We can either draw the background from and image, of render it on each update
        if self.board_image is not None:
            self.screen.blit(self.board_image, (HEADER_LEFT, HEADER_TOP))
        else:
            self.draw_board_squares(board)

        # highlight move history
        if self.move_history:
            self.highlight_squares(
                self.move_history[-1].locations,
                self.move_history[-1].locations[0],
                color=HIGH2,
            )

        if self.time:
            for player_type, player_time in self.time.items():
                message = time_to_str(player_time)
                left = (player_type == BLACK_PLAYER) * (
                    HEADER_LEFT + BOARD_WIDTH
                ) + MARGIN
                self.draw_message(
                    message, left=left, top=HEADER_TOP + MARGIN + LINE_HEIGHT
                )

        white_score = board.get_score(WHITE_PLAYER)
        black_score = board.get_score(BLACK_PLAYER)
        white_lead = white_score - black_score
        black_lead = black_score - white_score

        self.draw_message(
            str(white_lead), left=MARGIN, top=HEADER_TOP + MARGIN + 2 * LINE_HEIGHT
        )
        self.draw_message(
            str(black_lead),
            left=HEADER_LEFT + BOARD_WIDTH + MARGIN,
            top=HEADER_TOP + MARGIN + 2 * LINE_HEIGHT,
        )

        if (self.legal_moves is not None) and (self.selected_piece is not None):
            self.highlight_squares(
                self.legal_moves, self.selected_piece, shape="circle"
            )

        self.draw_board_pieces(board)

        pygame.display.update()
        self.clock.tick(self.fps)

    def draw_board_squares(self, board):
        """
        Takes a board object and draws all of its squares to the display
        """
        for x in range(2 * board.width):
            for y in range(2 * board.height):
                if (x + y) % 2:
                    self.draw_board_square(x, y, COLOR_DARK_SQUARE)
                else:
                    self.draw_board_square(x, y, COLOR_LIGHT_SQUARE)

    def draw_board_square(self, x, y, color):
        """draw a square on the board"""
        text_surface_obj = None
        if (x + y) % 2:
            i = matrix_to_list_coords((x, y))
            text_surface_obj = self.font.render(
                "%d" % i, True, COLOR_LIGHT_SQUARE, color
            )

        pygame.draw.rect(
            self.screen,
            color,
            tuple(map(int, pixel_coords((x, y), do_center=False)))
            + (self.square_width, self.square_height),
        )

        if text_surface_obj is not None:
            self.screen.blit(
                text_surface_obj, tuple(map(int, pixel_coords((x, y), do_center=False)))
            )

    def draw_board_circle(self, x, y, color):
        """Draw a circle on the board"""
        pygame.draw.circle(
            self.screen,
            color,
            tuple(map(int, pixel_coords((x, y)))),
            int(self.piece_size // 2),
        )

    def draw_board_pieces(self, board):
        """
        Takes a board object and draws all of its pieces to the display
        """
        for player, player_pieces in board.pieces.items():
            for i in player_pieces:
                xy = list_to_matrix_coords(i)
                self.draw_board_piece(xy[0], xy[1], player, player_pieces[i])
                continue

    def draw_board_piece(self, x, y, color, is_king):
        if color == WHITE_PLAYER:
            edge_color = COLOR_BLACK_PLAYER
            fill_color = COLOR_WHITE_PLAYER
        else:
            edge_color = COLOR_BLACK_PLAYER
            fill_color = COLOR_BLACK_PLAYER

        pygame.draw.circle(
            self.screen,
            fill_color,
            tuple(map(int, pixel_coords((x, y)))),
            int(self.piece_size),
        )

        pygame.draw.circle(
            self.screen,
            edge_color,
            tuple(map(int, pixel_coords((x, y)))),
            int(self.piece_size),
            3,
        )

        if is_king:
            pygame.draw.circle(
                self.screen,
                GOLD,
                tuple(map(int, pixel_coords((x, y)))),
                int(self.piece_size // 1.7),
                int(self.piece_size // 4),
            )

    def highlight_squares(self, indexes, origin=None, color=None, shape="square"):
        """
                Squares is a list of board coordinates.
        highlight_squares highlights them.
        """
        if color is None:
            color = HIGH

        if shape == "square":
            draw = self.draw_board_square
        elif shape == "circle":
            draw = self.draw_board_circle

        for index in indexes:
            xy = list_to_matrix_coords(index)
            draw(xy[0], xy[1], color)

        if origin != None:
            xy = list_to_matrix_coords(origin)
            draw(xy[0], xy[1], color)

    def draw_message(
        self,
        message,
        text_color=COLOR_LIGHT_SQUARE,
        background_color=COLOR_BLACK_PLAYER,
        top=None,
        left=None,
        center=None,
    ):
        """
        Draws message to the screen.
        """
        text_surface_obj = self.font.render(message, True, text_color, background_color)
        text_rect_obj = text_surface_obj.get_rect()

        if top is not None:
            text_rect_obj.top = top

        if left is not None:
            text_rect_obj.left = left

        if center is not None:
            text_rect_obj.center = center

        self.screen.blit(text_surface_obj, text_rect_obj)

        # self.message = True
        # self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
        # self.text_surface_obj = self.font_obj.render(message, True, HIGH, COLOR_DARK_SQUARE)
        # self.text_rect_obj = self.text_surface_obj.get_rect()
        # self.text_rect_obj.center = (self.window_width // 2, self.window_height // 2)
