import piecedata
import whitesetup
import blacksetup
import random
from pprint import pprint

class Chess:
    
    @staticmethod   
    def nametocoord(s):  
        return (ord(s[0]) - 97, int(s[1]) - 1)
    
    @staticmethod
    def coordtoname(x, y):
        return f'{chr(x + 97)}{y + 1}'
    
    class InvalidStartingPosition(Exception):
        pass
    
    class InvalidMove(Exception):
        pass

    class Pieces:
        
        def syntax_init(self, color, coordinates, parent):
            
            Chess.Pieces.__init__(self, color, coordinates, parent)
            
            if self.color == 'black':
                if color == 'black':
                    self.movements = {
                        (tile[0], -tile[1], tile[2]): [
                            (move[0], -move[1], move[2])
                            for move in moves
                        ]
                        for tile, moves in self.movements.items()
                    }
        
        def __init__(self, color, coordinates, parent):
            self.color = color
            self.coordinates = coordinates
            self.found_path = False
            self.parent = parent
            if self.parent.squares[self.coordinates]['piece'] == None:
                self.parent.squares[self.coordinates]['piece'] = self
            else:
                raise InvalidStartingPosition
            
        def move(self, newcoordinates):
            self.parent.squares[self.coordinates]['piece'] = None
            self.parent.squares[newcoordinates]['piece'] = self
            self.coordinates = newcoordinates
            self.found_path = True
            
        def attempt_move(self, end, start=(0, 0, 'start'), visited=None):
            if visited  == None:
                visited = set()
            visited.add((self.coordinates[0]+start[0], self.coordinates[1]+start[1], start[2]))
            
            if not self.found_path:
                for i in self.movements[start]:
                    newcoord = (self.coordinates[0]+i[0], self.coordinates[1]+i[1])
                    
                    if newcoord in visited:
                        continue
                    visited.add(newcoord)
                    if newcoord not in self.parent.squares:
                        continue
                    if not self.parent.squares[newcoord]['isActive']:
                        continue
                    
                    if self.parent.squares[newcoord]['piece']:
                        if i[2] in {'attack', 'capture', 'telefrag', 'teleport'}:
                            if (self.parent.squares[newcoord]['piece'].color != self.color) and newcoord == end:
                                self.move(newcoord)
                                if self.parent.parent.isAtomic:
                                    for k in [(-1, 1),  (0, 1),  (1, 1),
                                              (-1, 0),           (1, 0),
                                              (-1, -1), (0, -1), (1, -1)]:
                                        if not isinstance(self.parent.squares[(self.coordinates[0] + k[0], self.coordinates[1] + k[1])]['piece'], Chess.Frontrank):
                                            self.parent.squares[(self.coordinates[0] + k[0], self.coordinates[1] + k[1])]['piece'] == None

                        if (i[2] == 'phase' or i[2] == 'teleport' or i[2] == 'telefrag') and newcoord != end:
                            for j in self.movements[i]:
                                if j not in visited:
                                    self.attempt_move(end, start=i, visited=visited)
                    else:
                        if newcoord != end:
                            try:
                                for j in self.movements[i]:
                                    if j not in visited:
                                        self.attempt_move(end, start=i, visited=visited)
                            except KeyError:
                                pass
                        elif i[2] in {'move', 'attack', 'phase', 'teleport'}:
                                self.move(newcoord)
                                    
                if start == (0, 0, 'start') and self.found_path == True:
                    if self.parent.parent.turn == 'white':
                        self.parent.parent.turn = 'black'
                    else:
                        self.parent.parent.turn = 'white'
                    self.found_path = False
            

    class Frontrank(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[0] != 1) or (self.color == 'black' and coordinates[0] != 6):
                raise InvalidStartingPosition

    class Backrank(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[0] != 0) or (self.color == 'black' and coordinates[0] != 7):
                raise Chess.InvalidStartingPosition

    class Leader(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[0] != 0) or (self.color == 'black' and coordinates[0] != 7):
                raise Chess.InvalidStartingPosition

    class Board:
    
        def __init__(self, parent):
            self.squares = {}
            self.parent = parent
            
            for i in range(64):
                self.squares[(i // 8, i % 8)] = {
                    'piece': None,
                    'isActive': True}
            
            if None in whitesetup.arrangement.values() or None in blacksetup.arrangement.values():
                raise InvalidStartingPosition
            
            for square, piece in whitesetup.arrangement.items():
                self.squares[Chess.nametocoord(square)]['piece'] = parent.piece_name_to_class[piece]('white', Chess.nametocoord(square), self)
                
            for square, piece in blacksetup.arrangement.items():
                self.squares[Chess.nametocoord(square)]['piece'] = parent.piece_name_to_class[piece]('black', Chess.nametocoord(square), self)

            if parent.isRandom:
                self.shuffle()
             
        def shuffle(self):
            order = list(range(8))
            old = [[self.squares[(x, y)]['piece'] for x in range(8)] for y in [0, 1, 6, 7]]
            
            random.shuffle(order)
            
            for new_pos, old_pos in enumerate(order):
                for y in range(4):
                    self.squares[(new_pos, [0, 1, 6, 7][y])]['piece'] =  old[y][old_pos]
                    
            for x in range(8):
                for y in [0, 1, 6, 7]:
                    self.squares[(x, y)]['piece'].coordinates = (x, y)

    class Game:

        def __init__(self, isRandom, isAtomic, maxvalues):
            
            self.turn = 'white'
            self.isRandom = isRandom
            self.isAtomic = isAtomic
            self.maxvalues = maxvalues
            
            self.piece_name_to_class = {}
            
            self.role_to_class = {
                "Frontrank": Chess.Frontrank,
                "Backrank": Chess.Backrank,
                "Leader": Chess.Leader
                }
            
            for i in piecedata.piecedata:
                
                piece_type = type(i['name'], (self.role_to_class[i['role']],), {
                    'value': i['value'],
                    'movements': i['movements'],
                    '__init__': Chess.Pieces.syntax_init
                })
                
                self.piece_name_to_class[f"{i['name']}"] = piece_type

            self.board = Chess.Board(self)
            
        def input_to_move(self, coordinates1, coordinates2):
            obj = self.board.squares[coordinates1]['piece']
            if obj == None:
                raise Chess.InvalidMove
            elif obj.color != self.turn or self.board.squares[coordinates2]['isActive'] == False:
                raise Chess.InvalidMove
            else:
                obj.attempt_move(coordinates2)
                
game = Chess.Game(False, True, 91)
game.input_to_move((4, 1), (4, 2))
print(game.board.squares[(4, 2)])
game.input_to_move((4, 6), (4, 5))
print(game.board.squares[(4, 5)])
game.input_to_move((6, 0), (5, 2))
print(game.board.squares[(5, 2)])
game.input_to_move((4, 5), (4, 4))
print(game.board.squares[(4, 4)])
game.board.squares[(5, 4)] == game.piece_name_to_class['Knight']('black', (5, 4), game.board)
print(game.board.squares[(5, 4)])
game.input_to_move((5, 2), (4, 4))
print(game.board.squares[(4, 4)])
print(game.board.squares[(5, 4)])