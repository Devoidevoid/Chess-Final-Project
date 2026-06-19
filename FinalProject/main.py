import chess
from pprint import pprint

game = chess.Chess.Game(False, False, 700)

pprint(game.board.squares)
print(game.turn)
game.input_to_move((4, 1), (4, 2))
print(game.board.squares[(4, 2)]['piece'])
print(game.turn)