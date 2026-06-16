import piecedata
import whitesetup
import blacksetup
from pprint import pprint

class Chess():
    
    def __init__(self):
        self.board = self.Board()
        self.turn = 'white'
        self.piece_name_to_class = {}
        
        role_to_class = {
            "Frontrank": self.Frontrank,
            "Backrank": self.Backrank,
            "Leader": self.Leader
            }
        
        def syntax_init(self, color, coordinates):
            super().__init__(color, coordinates)
            if self.color == 'black':
                if color == 'black':
                    self.movements = {
                        (tile[0], -tile[1], tile[2]): [
                            (move[0], -move[1], move[2])
                            for move in moves
                        ]
                        for tile, moves in self.movements.items()
                    }
        
        for i in piecedata.piecedata:
            piece_type = type(i['name'], (role_to_class[i['role']],), {
                'value': i['value'],
                'movements': i['movements'],
                '__init__': syntax_init
            })
            self.piece_name_to_class[f"{i['name']}"] = piece_type
    
    @staticmethod   
    def nametocoord(s):  
        return (ord(s[0]) - 97, int(s[1]) - 1)
    
    @staticmethod
    def coordtoname(x, y):
        return f'{chr(x + 97)}{y + 1}'
    
    @staticmethod
    def input_to_move(coordinates1, coordinates2):
        obj = Chess.Board.squares[coordinates1['piece']]
        if obj == None:
            pass
        elif obj.color != turn or Chess.Board.squares[coordinates2['isActive']] == False:
            pass
        else:
            obj.attempt_move(coordinates2)
    
    class Board:
    
        def __init__(self):
            self.squares = {}
            
            for i in range(64):
                self.squares[(i // 8, i % 8)] = {
                    'piece': None,
                    'isActive': True}
                
            for square, piece in whitesetup.arrangement.items():
                self.squares[chess.nametocoord(square)]['piece'] = self.piece_name_to_class[piece]('white', chess.nametocoord(square))
                
            for i in blacksetup.arrangement:
                self.squares[chess.nametocoord(square)]['piece'] = self.piece_name_to_class[piece]('black', chess.nametocoord(square))
        
    class Piece:
        # load each piece from another file
        
        def __init__(self, color, coordinates):
            self.color = color
            self.coordinates = coordinates
            self.found_path = False
            if Chess.Board.squares[coordinates['piece']] == None:
                Chess.Board.squares[coordinates['piece']] = self
            else:
                raise InvalidStartingPosition
            
        def move(self, newcoordinates):
            Chess.Board.squares[self.coordinates['piece']] = None
            Chess.Board.squares[newcoordinates['piece']] = self
            self.coordinates = newcoordinates
            self.found_path = True
            
        def attempt_move(self, end, start=(0, 0, 'start'), visited=None):
            if visited  == None:
                visited = set()
            visited.add(self.coordinates)
            
            if not self.found_path:
                for i in self.movements[start]:
                    newcoord = (self.coordinates[0]+i[0], self.coordinates[1]+i[1])
                    
                    if newcoord in visited:
                        continue
                    visited.add(newcoord)
                    if newcoord not in Chess.Board.squares:
                        continue
                    
                    if Chess.Board.squares[newcoord['piece']]:
                        if i[2] in {'attack', 'capture', 'telefrag', 'teleport'}:
                            if (Chess.Board.squares[newcoord['piece']].color != self.color) and newcoord == end:
                                self.move(newcoord)
                        if (i[2] == 'phase' or i[2] == 'teleport' or i[2] == 'telefrag') and newcoord != end:
                            for j in self.movements[i]:
                                if j not in visited:
                                    attempt_move(end, start=i, visited=visited)
                    else:
                        if newcoord != end:
                            for j in self.movements[i]:
                                if j not in visited:
                                    attempt_move(end, start=i, visited=visited)
                        elif i[2] in {'move', 'attack', 'phase', 'teleport'}:
                                self.move(newcoord)
                                    
                if start == (0, 0, 'start') and self.found_path == True:
                    if Chess.turn == 'white':
                        Chess.turn = 'black'
                    else:
                        Chess.turn = 'white'
                    self.found_path = False
            
    class Frontrank(Piece):
        
        def __init__(self, color, coordinates):
            super().__init__(color, coordinates)
            if (self.color == 'white' and coordinates[0] != 1) or (self.color == 'black' and coordinates[0] != 6):
                raise InvalidStartingPosition
          
    class Backrank(Piece):
        
        def __init__(self, color, coordinates):
            super().__init__(color, coordinates)
            if (self.color == 'white' and coordinates[0] != 0) or (self.color == 'black' and coordinates[0] != 7):
                raise InvalidStartingPosition
        
    class Leader(Piece):
        
        def __init__(self, color, coordinates):
            super().__init__(color, coordinates)
            if (self.color == 'white' and coordinates[0] != 0) or (self.color == 'black' and coordinates[0] != 7):
                raise InvalidStartingPosition
    
    class InvalidStartingBoard(Exception):
        pass

game = Chess()
pprint(game.board.squares)
print(game.nametocoord('a8'))