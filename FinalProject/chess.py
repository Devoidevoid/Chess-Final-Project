# This file was created entirely by Devoidevoid, and tested by saltfishy7
# Imports of other data necessary for custom setup, as well as random module for chess960.
import piecedata
import whitesetup
import blacksetup
import random

# All of the logic is encapsulated in a single class called Chess, which only contains static methods and other classes.
class Chess:
    
    # Converts the name of a square on a chess board to a file, rank tuple with both ranging 0-7 (eg. e4 -> 4, 3)
    @staticmethod   
    def nametocoord(s):  
        return (ord(s[0]) - 97, int(s[1]) - 1)
    
    # Not used in the chess implementation, but acts as a theoretical inverse function to nametocoord(s)
    @staticmethod
    def coordtoname(x, y):
        return f'{chr(x + 97)}{y + 1}'
    
    # An exception that is raised when the starting position of a game would violate the rules.
    class InvalidStartingPosition(Exception):
        pass

    # This class consolidates the main behaviors of pieces, and is the parent to the 3 role classes.
    class Pieces:
        
        # IMPORTANT
        # All uses of the parameter 'parent' inside of an __init__ method do not refer to a literal parent class,
        # but a class that needs to be frequently accessed inside of it, such as how pieces frequently use the board.

        # The purpose of this function is to be injected
        def syntax_init(self, color, coordinates, parent):
            
            # 
            Chess.Pieces.__init__(self, color, coordinates, parent)
            
            if self.color == 'black':
                self.movements = {
                    (tile[0], -tile[1], tile[2]): [
                        (move[0], -move[1], move[2])
                        for move in moves
                    ]
                    for tile, moves in self.movements.items()
                }
        
        def __init__(self, color, coordinates, parent):
            self.movements = self.refmovements.copy()
            self.color = color
            self.coordinates = coordinates
            self.found_path = False
            self.parent = parent
            if self.parent.squares[self.coordinates]['piece'] == None:
                self.parent.squares[self.coordinates]['piece'] = self
            else:
                raise Chess.InvalidStartingPosition
            
        def move(self, newcoordinates):
            self.parent.squares[self.coordinates]['piece'] = None
            self.parent.squares[newcoordinates]['piece'] = self
            self.coordinates = newcoordinates
            self.found_path = True
            if isinstance(self, Chess.Frontrank):

                self.movements = self.newmovements
                if self.color == 'black':
                    self.movements = {
                        (tile[0], -tile[1], tile[2]): [
                            (move[0], -move[1], move[2])
                            for move in moves
                        ]
                        for tile, moves in self.movements.items()
                    }

                if self.color == 'white' and self.coordinates[1] == 7:
                    self.parent.squares[self.coordinates]['piece'] = None
                    self.parent.squares[self.coordinates]['piece'] = self.parent.parent.piece_name_to_class[self.promotion]('white', self.coordinates, self.parent)
                if self.color == 'black' and self.coordinates[1] == 0:
                    self.parent.squares[self.coordinates]['piece'] = None
                    self.parent.squares[self.coordinates]['piece'] = self.parent.parent.piece_name_to_class[self.promotion]('black', self.coordinates, self.parent)
                

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
                                            self.parent.squares[(self.coordinates[0] + k[0], self.coordinates[1] + k[1])]['piece'] = None
                                    self.parent.squares[self.coordinates]['piece'] = None

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
            if (self.color == 'white' and coordinates[1] != 1) or (self.color == 'black' and coordinates[1] != 6):
                raise Chess.InvalidStartingPosition

    class Backrank(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[1] != 0) or (self.color == 'black' and coordinates[1] != 7):
                raise Chess.InvalidStartingPosition

    class Leader(Pieces):
        def __init__(self, color, coordinates, parent):
            if any(isinstance(i['piece'], Chess.Leader) for i in parent.squares.values()):
                raise Chess.InvalidStartingPosition
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[1] != 0) or (self.color == 'black' and coordinates[1] != 7):
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
                raise Chess.InvalidStartingPosition
            
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
                    'promotion': i['promotion'],
                    'refmovements': i['movements'],
                    'newmovements': i['newmovements'],
                    '__init__': Chess.Pieces.syntax_init
                })
                
                self.piece_name_to_class[f"{i['name']}"] = piece_type

            self.board = Chess.Board(self)
            
        def input_to_move(self, coordinates1, coordinates2):
            obj = self.board.squares[coordinates1]['piece']
            if obj == None:
                pass
            elif obj.color != self.turn or self.board.squares[coordinates2]['isActive'] == False:
                pass
            else:
                obj.attempt_move(coordinates2)

            return self.winner()

        def winner(self):
            for l in ['black', 'white']:
                if not any(isinstance(m['piece'], Chess.Leader) and m['piece'].color == l for m in self.board.squares.values()):
                    if l == 'black':
                        return 'white'
                    else:
                        return 'black'
            return None

                
game = Chess.Game(False, False, 91)
game.input_to_move((4, 1), (4, 3))
game.input_to_move((3, 6), (3, 4))
game.input_to_move((4, 3), (3, 4))
game.input_to_move((4, 7), (3, 6))
game.input_to_move((4, 0), (4, 1))
game.input_to_move((3, 6), (4, 5))
game.input_to_move((3, 4), (4, 5))