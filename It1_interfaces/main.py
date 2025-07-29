from pathlib import Path
from Board import Board
from Img import Img
from Screen import Screen

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"
    photos_root = base_path.parent / "photos"

    board = Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=Img().read("../board.png", size=(640, 640))
    )
    images : dict[str, Img] = {
        'opening_img': Img().read(photos_root / "opening_image.jpg", size=(780, 1600)),
        'black_victory': Img().read(photos_root / "black_victory.jpg", size=(780, 1600)),
        'white_victory': Img().read(photos_root / "white_victory.jpg", size=(780, 1600))

    }
    screen = Screen(images, ['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))

    from Game import Game
    game = Game(screen, board, pieces_root, placement_csv, sounds_root)
    game.run()
