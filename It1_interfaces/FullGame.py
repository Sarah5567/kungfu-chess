import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_SIZE = 800
SQUARE_SIZE = WINDOW_SIZE // 8
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chess Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (128, 128, 128)

# Load chess pieces
pieces = {}
piece_types = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
colors = ['black', 'white']

for color in colors:
    for piece in piece_types:
        try:
            pieces[f"{color}_{piece}"] = pygame.image.load(f"chess_pieces/{color}_{piece}.png")
            pieces[f"{color}_{piece}"] = pygame.transform.scale(pieces[f"{color}_{piece}"], (SQUARE_SIZE, SQUARE_SIZE))
        except:
            print(f"Could not load {color}_{piece}.png")
    pieces[f"{color}_pawn"] = pygame.image.load(f"chess_pieces/{color}_pawn.png")
    pieces[f"{color}_pawn"] = pygame.transform.scale(pieces[f"{color}_pawn"], (SQUARE_SIZE, SQUARE_SIZE))

# Initial board setup
board = [
    ['black_rook', 'black_knight', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', 'black_knight', 'black_rook'],
    ['black_pawn'] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ['white_pawn'] * 8,
    ['white_rook', 'white_knight', 'white_bishop', 'white_queen', 'white_king', 'white_bishop', 'white_knight', 'white_rook']
]

selected_piece = None
selected_pos = None

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[row][col]
            if piece:
                try:
                    screen.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))
                except:
                    print(f"Could not draw {piece}")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            row = y // SQUARE_SIZE
            col = x // SQUARE_SIZE
            
            if selected_piece:
                # Move the piece
                board[row][col] = selected_piece
                board[selected_pos[0]][selected_pos[1]] = None
                selected_piece = None
                selected_pos = None
            else:
                # Select the piece
                if board[row][col]:
                    selected_piece = board[row][col]
                    selected_pos = (row, col)

    screen.fill((0, 0, 0))
    draw_board()
    pygame.display.flip()

pygame.quit()
sys.exit()
