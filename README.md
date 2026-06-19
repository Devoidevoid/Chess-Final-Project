# Final Project for Foundations of Computer Science

A chess game built in Python with pygame, supporting multiple variants. The game features drag-and-drop piece movement, full move validation, and three game modes.

## Features
- Standard Chess with (near) full move validation
- Chess960 (Fischer Random) — randomized back-rank starting position
- Atomic Chess — captures cause an explosion that destroys surrounding pieces
- Drag-and-drop piece movement with a custom cursor
- Move highlighting on hover
- Algebraic notation printed to the console for each move
- Sound effects and background music

## Work in Progress
- Full move validation (i.e., two-square advance on pawn's first move)
- Win detection with a victory screen (as shown in ChessMechanics.py, but with the new engine)

## Future Goals
- Custom piece packaging
- Advanced chess rulings (stalemate detection, en passant, underpromotion, castling)
- Additional variants (?)
- General QoL updates (move tracker, clock, etc.)

## Requirements
- Python 3
- pygame-ce

## Run Instructions
Run the main file: python main.py
Select a variant from the menu (Standard, Chess960, or Atomic), then play.

## Controls
- Click and drag a piece to move it
- Release on a destination square to make a move (illegal moves snap back)
- Escape — quit the game

## Architecture
The project is largely divided into two halves.

The game engine (`chess.py`) is the source of truth for the board state. It validates moves, enforces turn order, and handles captures. Pieces and their movement rules are defined in `Piecemoves.py`.

The frontend (`main.py`) handles all rendering and input — the board, pieces, drag-and-drop, sounds, and menus. After each move, it asks the engine for the legality of the move and resyncs the display to match the engine's board.

The two coordinate systems differ (invertedly) on the vertical axis — the frontend's row 0 is the top, while the engine's y=0 is the bottom — so a conversion is applied at the boundary between them.

## File Overview
- `main.py` — pygame frontend (rendering, input, sound)
- `chess.py` — chess engine (move validation, board state)
- `Piecemoves.py` — piece definitions and movement rules
- `whitesetup.py` / `blacksetup.py` — starting positions
- `imagemedia/` — piece sprites, cursor, fonts, background
- `audiomedia/` — sound effects and music

> **Note:** ChessMechanics.py is a file used during the development stages for the majority of the project. It runs without logic checks, so any move is possible — this makes it more permissive and useful for demonstrating most of the UI's capabilities independent of the engine.

## Notes
The `Game` constructor takes a third argument (`maxvalues`) reserved for a potential future feature involving custom pieces. It is currently unused.

## Attributions
- **Background image:** Windows XP "Bliss" wallpaper
- **Chess set:** cburnett on Wikipedia, used under Creative Commons
- **Music:** Wii Sports and Mii Channel music (Nintendo) — used for educational purposes
- **Sound effects:** taken from public soundboards

## Credits
- **saltfishy7** — frontend coding and integrations, accessories and UI/UX
- **devoidevoid** — backend coding and logic
