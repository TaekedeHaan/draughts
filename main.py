import pydraughts
from pydraughts import BLACK_PLAYER, WHITE_PLAYER


def main():
    player1 = pydraughts.bots.RandomWalker()
    player2 = pydraughts.human_player.HumanPlayer()

    game = pydraughts.Game(player1=player1, player2=player2, do_multi_thread=True)
    game.play()


if __name__ == "__main__":
    main()
