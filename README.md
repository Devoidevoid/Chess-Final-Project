Final Project for Foundations of Computer Science
A chess game built in Python with pygame, supporting multiple variants. The game features drag-and-drop piece movement, full move validation and three game modes. 

Features 
- Standard Chess with (near) full move validation
- Chess960 (Fischer Random) - randomized back-rank starting position
- Atomic Chess - captures cause an explosion that destroys surrounding pieces
- Drag-and-drop piece movement with a custom cursor
- Move highlighting on hover
- Algebraic notation printed to the console for each move
- Sound effects and background music

WIP:
- Full move validation (ie, two square advance on pawn first move)
- Win detection with a victory screen (as shown in ChessMechanics.py, but with new engine)

Future Goals:
- Custom piece packaging
- Advanced Chess rulings (determining stalemate, en passant, underpromotion, castling)
- Additional variants (?)
- General QoL updates (move tracker, clock, etc.)

Requirements
- Python 3
- Pygame-CE

Run Instructions
Run the main file: python main.py
Select a variant from the menu (Standard, Chess960, or Atomic) then play.

Controls:
Click and drag a piece to move it
Release on a destination square to make a move (illegal moves snap back)
Escape -- quit the game

Architecture:
The project is largely divided into two halves.
The game engine (game.py) is the source of truth for the board state. It validates moves, enforces turn order and handles captures. Pieces and their movement rules are defined in Piecemoves.py.
The frontend (main.py) handles all rendering and input - the board, pieces, drag-and-drop, sounds, and menus. After each move, it asks the engine for the legality of the such move and resyncs the display to match the engine's board.

The two coordinate systems differe (invertedly) on the vertical axis (the frontend's row 0 is the top, engine's y=0 is on the bottom), so a conversion is applied at the boundary between them.

File Overview:
main.py - pygame frontend (rendering, input, sound)
chess.py - chess engine (move validation, board state)
Piecemoves.py - piece definitions and movement rules
whitesetup.py/blacksetup.py - starting positions
**NOTE: ChessMechanics.py is a file that was used in development stages for a majority of the project. It works unchecked with free logic, so any move is possible, but it is far more intuitive (as any move is possible) and demonstrates most capabilities of the UI without logic.**
imagemedia/ - piece sprites, cursor, fonts, background
audiomedia/ - sound effects and music

Notes:
The Game constructor takes a third argument (maxvalues) reserved for a potential future feature involving custom pieces. It is currently unused.

Attributions:
Background Image: Windows XP "bliss" background
Chess Set: cburnett on Wikipedia, using under CC
Music - Taken from Nintendo under CC, Wii Sports and Mii Channel music used
Sound effects taken from public soundboards

Credits:
saltfishy7 - frontend coding and integrations, accessories and UI/UX
devoidevoid - backend coding and logic
