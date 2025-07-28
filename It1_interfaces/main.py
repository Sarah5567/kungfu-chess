from pathlib import Path
from Board import Board
from Img import Img
from Screen import Screen

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"

    board = Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=Img().read("../board.png", size=(640, 640))
    )

    screen = Screen(['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))

    from Game import Game
    game = Game(screen, board, pieces_root, placement_csv, sounds_root)
    game.run()
