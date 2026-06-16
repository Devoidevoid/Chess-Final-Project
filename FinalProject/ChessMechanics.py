import pygame
import random as rand

# Setup
pygame.init()
clock = pygame.time.Clock()

# Game Screen
screen_height = 1000
screen_width = int(screen_height * 16/10)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game")

# Background Setup
bg_img = pygame.image.load('bliss.jpg').convert()

# Title Screen Setup
button_standard = pygame.Rect(screen_width//2 - 150, screen_height//2 - 100, 300, 70)
button_chess960 = pygame.Rect(screen_width//2 - 150, screen_height//2, 300, 70)
button_atomic   = pygame.Rect(screen_width//2 - 150, screen_height//2 + 100, 300, 70)

title_font = pygame.font.Font('Quicksand-Bold.ttf', 90)
menu_font = pygame.font.Font('Quicksand-Regular.ttf', 50)

# Music Player
pygame.mixer.music.load("mii.mp3")
pygame.mixer.music.play()
wilhelm = pygame.mixer.Sound('wilhelm.mp3')
click = pygame.mixer.Sound('click.mp3')
explosion = pygame.mixer.Sound('kaboom.mp3')
victory_sound = pygame.mixer.Sound('fivebigbooms.mp3')
# Cursor
cursor_img = pygame.image.load('cursor1.png').convert_alpha()
pygame.mouse.set_visible(False)  # hide real cursor

# Startscreen Loop
variant = None
while variant is None:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_standard.collidepoint(mx, my):
                variant = "standard"
            elif button_chess960.collidepoint(mx, my):
                variant = "chess960"
            elif button_atomic.collidepoint(mx, my):
                variant = "atomic"

    screen.blit(bg_img, (0, 0))
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(120)  # a higher value makes the darkened effect much stronger
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    title = title_font.render("Chess", True, (255, 255, 255))
    screen.blit(title, (screen_width//2 - title.get_width()//2, 150))

    for rect, label in [(button_standard, "Standard"), (button_chess960, "Chess960"), (button_atomic, "Atomic")]:
        pygame.draw.rect(screen, (80, 80, 100), rect, border_radius=8)
        text = menu_font.render(label, True, (255, 255, 255))
        screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

    screen.blit(cursor_img, (mx - 5, my - 5))
    pygame.display.update()
    clock.tick(60)

# Square Settings, Board Center
TILE = 80 # Tile/Square Length is 80
board_x_offset = (screen_width - 8 * TILE) // 2
board_y_offset = (screen_height - 8 * TILE) // 2

# Piece Building + Piece Rect Following

images = {}

class Piece:
    def __init__(self, image_path, col, row):
        name = image_path.replace(".png", "")
        self.color = name.split("_")[0]
        self.kind = name.split("_")[1]   
        if image_path not in images:
            img = pygame.image.load(image_path).convert_alpha()
            images[image_path] = pygame.transform.scale(img, (TILE, TILE))
        self.img = images[image_path]
        self.rect = pygame.Rect(board_x_offset + col * TILE, board_y_offset + row * TILE, TILE, TILE)
        self.held = False
    def draw(self, screen):
        screen.blit(self.img, self.rect.topleft)

sides = ["black", "white"]
piece_names = ["pawn", "bishop", "knight", "rook", "queen", "king"]

for side in sides:
    for name in piece_names:
        path = f"{side}_{name}.png"
        img = pygame.image.load(path).convert_alpha()
        images[path] = pygame.transform.scale(img, (TILE, TILE))
        
# Starting board layout
starting_board = [
    ["black_rook",   "black_knight", "black_bishop", "black_queen", "black_king",  "black_bishop", "black_knight", "black_rook"],
    ["black_pawn",   "black_pawn",   "black_pawn",   "black_pawn",  "black_pawn",  "black_pawn",   "black_pawn",   "black_pawn"],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ["white_pawn",   "white_pawn",   "white_pawn",   "white_pawn",  "white_pawn",  "white_pawn",   "white_pawn",   "white_pawn"],
    ["white_rook",   "white_knight", "white_bishop", "white_queen", "white_king",  "white_bishop", "white_knight", "white_rook"],
]

# Optional Chess960 Block of Code
if variant == "chess960":
    backrow = ["black_rook",   "black_knight", "black_bishop", "black_queen", "black_king",  "black_bishop", "black_knight", "black_rook"]
    frontrow = ["white_rook",   "white_knight", "white_bishop", "white_queen", "white_king",  "white_bishop", "white_knight", "white_rook"]
    orderlist = [1, 2, 3, 4, 5, 6, 7, 8]
    legality = False
    while legality == False:
        rand.shuffle(orderlist)
        if orderlist.index(3) % 2 != orderlist.index(6) % 2:
            legality = True
    newbackrow = []
    for term in orderlist:
        newbackrow.append(backrow[term - 1])
    newfrontrow = []
    for term in orderlist:
        newfrontrow.append(frontrow[term - 1])

    starting_board[0] = newbackrow
    starting_board[7] = newfrontrow

# Generate pieces list from board
pieces = []
for row in range(8):
    for col in range(8):
        name = starting_board[row][col]
        if name:
            pieces.append(Piece(f"{name}.png", col, row))


lettercords = ["a", "b", "c", "d", "e", "f", "g", "h"]
numcords = ["1", "2", "3", "4", "5", "6", "7", "8"]
numcords.reverse()

notation = {
    "pawn": "",
    "rook": "R",
    "knight": "N",
    "bishop": "B",
    "queen": "Q",
    "king": "K"
}

game_over = False
winner = ""

# Game Run Loop
movecount = 0
lastmove = "black"
movenotation = ""
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
# terminating game when quit
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for p in pieces:
                if p.rect.collidepoint(mx, my):  # checking if box was clicked
                    p.held = True
                    from_col = (p.rect.x - board_x_offset) // TILE
                    from_letcord = lettercords[int(from_col)]
        capture = False
        if event.type == pygame.MOUSEBUTTONUP:
            for p in pieces:
                if p.held:
                     if lastmove == "black" and p.color == "white":
                         movecount += 1
                     col = (p.rect.x + TILE / 2 - board_x_offset) // TILE
                     row = (p.rect.y + TILE / 2 - board_y_offset) // TILE
                     col = max(0, min(7, col))
                     row = max(0, min(7, row))
                     letcord = lettercords[int(col)]
                     numcord = numcords[int(row)]
                     p.rect.topleft = (board_x_offset + col * TILE, board_y_offset + row * TILE)
                     recenttopleft = p.rect.topleft
                     piece_symbol = notation[p.kind]
                     if p.color == "white":
                         movenotation = f"{movecount}."
                     elif p.color == "black":
                         movenotation = f"{movecount}..."
                     lastmove = p.color
                     for i, other in enumerate(pieces):
                         if other.rect.topleft == recenttopleft and other.held == False:
                             if other.kind == "king":
                                 winner = "White" if other.color == "black" else "Black"
                                 game_over = True
                                 victory_sound.play()
                             pieces.pop(i)
                             capture = True
                             wilhelm.play()
                             if p.kind == "pawn":
                                 print(f"{movenotation} {from_letcord}x{letcord}{numcord}")
                             else:
                                 print(f"{movenotation} {piece_symbol}x{letcord}{numcord}")
                             if variant == "atomic" and capture:
                                 explosion.play()
                                 cx, cy = col, row
                                 piecesleft = []
                                 for piece in pieces:
                                     pcol = (piece.rect.x - board_x_offset) // TILE
                                     prow = (piece.rect.y - board_y_offset) // TILE
                                     exploded = abs(pcol - cx) <= 1 and abs(prow - cy) <= 1
                                     if exploded and piece.kind != "pawn":
                                         if piece.kind == "king":
                                            winner = "White" if piece.color == "black" else "Black"
                                            game_over = True
                                            victory_sound.play()
                                         continue
                                     piecesleft.append(piece)
                                 pieces = piecesleft
                                 if p in pieces:
                                     pieces.remove(p)
                     if capture == False:
                         click.play()
                         print(f"{movenotation} {piece_symbol}{letcord}{numcord}")
                     p.held = False
                     break
           

# setting piece to follow mouse
    for p in pieces:
        if p.held:
            p.rect.center = (mx, my)
            
    screen.blit(bg_img, (0, 0)) 

# building the board
    for row in range(8):
        for col in range(8):
            color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, color, (board_x_offset + col * TILE, board_y_offset + row * TILE, TILE, TILE))

# highlight the square under the mouse
    hover_col = (mx - board_x_offset) // TILE
    hover_row = (my - board_y_offset) // TILE
    if 0 <= hover_col < 8 and 0 <= hover_row < 8:
        highlight = pygame.Surface((TILE, TILE))
        highlight.set_alpha(60)  # transparency, 0-255
        highlight.fill((255, 255, 0))  # yellow
        screen.blit(highlight, (board_x_offset + hover_col * TILE, board_y_offset + hover_row * TILE))

    for p in pieces:
        if not p.held:
            p.draw(screen)

    for p in pieces:
        if p.held:
            p.draw(screen)
    
    if game_over:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        win_text = title_font.render(f"{winner} wins!", True, (255, 255, 255))
        screen.blit(win_text, (screen_width//2 - win_text.get_width()//2, screen_height//2 - win_text.get_height()//2))
        screen.blit(cursor_img, (mx - 5, my - 5))
        pygame.display.update()
        clock.tick(60)
        continue
    
    screen.blit(cursor_img, (mx - 5, my - 5)) # Draw Cursor at Mouse Position
    pygame.display.update()
    clock.tick(60)
pygame.quit()