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
        
        # Creates an instance of pieces with the following parameters
        def __init__(self, color, coordinates, parent):
            self.movements = self.refmovements.copy()
            self.color = color

            # Mirrors piece movements vertically for black
            if self.color == 'black':
                self.movements = {
                    (tile[0], -tile[1], tile[2]): [
                        (move[0], -move[1], move[2])
                        for move in moves
                    ]
                    for tile, moves in self.movements.items()
                }

            self.coordinates = coordinates
            self.parent = parent

            # Raises an invalid starting position exception if a piece's coordinates arent a valid tuple on the board
            # or are the location of an existing piece, barring the special case of promotion initializing without
            # numerical coordinates
            if self.coordinates != 'promotion':
                if self.parent.squares[self.coordinates]['piece'] == None:
                    self.parent.squares[self.coordinates]['piece'] = self
                else:
                    raise Chess.InvalidStartingPosition
            
            self.found_path = False
        
        # This function handles the literal process of moving a piece to a new square, and what happens directly after
        def move(self, newcoordinates):
            # Change location of piece on board as well as its own location attribute
            self.parent.squares[self.coordinates]['piece'] = None
            self.parent.squares[newcoordinates]['piece'] = self
            self.coordinates = newcoordinates
            self.found_path = True

            # Upon a front-rank (pawn) piece's first move (and later moves, but without effect), 
            # switches to future move pattern (no repeat double moves).
            if isinstance(self, Chess.Frontrank):

                # Mirrors new movement set for black
                self.movements = self.newmovements
                if self.color == 'black':
                    self.movements = {
                        (tile[0], -tile[1], tile[2]): [
                            (move[0], -move[1], move[2])
                            for move in moves
                        ]
                        for tile, moves in self.movements.items()
                    }

                # Handles promotion for black and white pieces; special use of 'promotion' instead of tuple corrdinates
                # to avoid any invalid syarting position errors.
                if self.color == 'white' and self.coordinates[1] == 7:
                    self.parent.squares[self.coordinates]['piece'] = None
                    self.parent.squares[self.coordinates]['piece'] = self.parent.parent.piece_name_to_class[self.promotion]('white', 'promotion', self.parent)
                    self.parent.squares[self.coordinates]['piece'].coordinates = self.coordinates
                if self.color == 'black' and self.coordinates[1] == 0:
                    self.parent.squares[self.coordinates]['piece'] = None
                    self.parent.squares[self.coordinates]['piece'] = self.parent.parent.piece_name_to_class[self.promotion]('black', 'promotion', self.parent)
                    self.parent.squares[self.coordinates]['piece'].coordinates = self.coordinates

        # This is the most complex function of the program, so it is important to note that piece movements are encoded
        # as a dictionary representing a directed graph. This function performs a depth-first search through this directed
        # graph to find if there is a valid path to the desired ending location.
        def attempt_move(self, end, start=(0, 0, 'start'), visited=None):

            # Initial recursive call of this function will create an empty set of visited squares.
            if visited  == None:
                visited = set()
            visited.add((self.coordinates[0]+start[0], self.coordinates[1]+start[1], start[2]))
            
            # If a path hasn't been found to the end yet, explores directed graph.
            if not self.found_path:
                for i in self.movements[start]:
                    # Newcoord is not on the directed graph, but a location on the board, as the nodes on the directed
                    # graph represent translations of the piece coordinates.
                    newcoord = (self.coordinates[0]+i[0], self.coordinates[1]+i[1])
                    
                    # Continue moves to the next node if a movement would take a piece to a visited square or outside the board.
                    if newcoord in visited:
                        continue
                    visited.add(newcoord)
                    if newcoord not in self.parent.squares:
                        continue

                    # isActive represents a feature of the program that currently has no use, but was planned to allow
                    # for the board to change in shape over time by toggling squares
                    if not self.parent.squares[newcoord]['isActive']:
                        continue
                    
                    # Move: Can end movement on an empty square, or walk through it
                    # Attack: Move or capture in one
                    # Capture: Can end movement only on occupied square, but walks through empty squares
                    # Phase: Like move, but can walk through pieces (unused)
                    # Teleport: Like attack, but can walk through pieces (unused)
                    # Telefrag: Like capture, but can walk through pieces (unused)

                    # Handles recursion and moving for every kind of movement by branching control flow
                    if self.parent.squares[newcoord]['piece']:
                        if i[2] in {'attack', 'capture', 'telefrag', 'teleport'}:
                            if (self.parent.squares[newcoord]['piece'].color != self.color) and newcoord == end:
                                self.move(newcoord)
                                # If a capture occurs in Atomic, blows up adjacent pieces and itself
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
                            # Handles case where a node does not have any movements out of it
                            except KeyError:
                                pass
                        elif i[2] in {'move', 'attack', 'phase', 'teleport'}:
                                self.move(newcoord)
                                    
                # On the outermost layer of recursion, flips the turn if a move was made, and returns found_path to False
                if start == (0, 0, 'start') and self.found_path == True:
                    if self.parent.parent.turn == 'white':
                        self.parent.parent.turn = 'black'
                    else:
                        self.parent.parent.turn = 'white'
                    self.found_path = False

    # All 3 of the below role classes follow the flow {piece kind} -> {role} > Pieces for inheritance

    # Defines starting necessity of Frontrank (pawn) pieces and is used in code to determine if a piece is Frontrank
    class Frontrank(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[1] != 1) or (self.color == 'black' and coordinates[1] != 6):
                raise Chess.InvalidStartingPosition
            
    # Defines starting necessity of Backrank pieces and is used in code to determine if a piece is Backrank
    class Backrank(Pieces):
        def __init__(self, color, coordinates, parent):
            super().__init__(color, coordinates, parent)
            if ((self.color == 'white' and coordinates[1] != 0) or (self.color == 'black' and coordinates[1] != 7)) and coordinates != 'promotion':
                raise Chess.InvalidStartingPosition

    # Defines starting necessity of Leader (king) pieces and ensures there is no more than one king per color as well as to identify kings.
    class Leader(Pieces):
        def __init__(self, color, coordinates, parent):
            if any((isinstance(i['piece'], Chess.Leader) and i['piece'].color == color) for i in parent.squares.values()):
                raise Chess.InvalidStartingPosition
            super().__init__(color, coordinates, parent)
            if (self.color == 'white' and coordinates[1] != 0) or (self.color == 'black' and coordinates[1] != 7):
                raise Chess.InvalidStartingPosition

    # Class representing the board behavior of Chess, instantiated by the Game class and often accessing it
    class Board:
    
        # Creates an empty board with 64 dictionaries, then uses the setup files to fill them in for each player
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

            # Shuffles piece positions in chess960
            if parent.isRandom:
                self.shuffle()
        
        # Used to shuffle piece positions in chess960
        def shuffle(self):
            order = list(range(8))
            # Double list comprehension in one line to create a 2d list of the original piece order
            old = [[self.squares[(x, y)]['piece'] for x in range(8)] for y in [0, 1, 6, 7]]
            
            random.shuffle(order)
            
            # Updates positions of pieces on board
            for new_pos, old_pos in enumerate(order):
                for y in range(4):
                    self.squares[(new_pos, [0, 1, 6, 7][y])]['piece'] =  old[y][old_pos]

            # Updates corrdinate attributes of pieces after shuffle. 
            for x in range(8):
                for y in [0, 1, 6, 7]:
                    self.squares[(x, y)]['piece'].coordinates = (x, y)

    # This class hosts important game behaviors and is solely initialized to create the entire logic of chess
    class Game:

        # Maxvalues is an unused parameter meant for custom pieces / board layouts, which were not created.
        def __init__(self, isRandom, isAtomic, maxvalues):
            
            # Sets the starting turn and variant of chess
            self.turn = 'white'
            self.isRandom = isRandom
            self.isAtomic = isAtomic
            self.maxvalues = maxvalues
            
            self.piece_name_to_class = {}
            
            # Assigns classes to string keys in a dictionary
            self.role_to_class = {
                "Frontrank": Chess.Frontrank,
                "Backrank": Chess.Backrank,
                "Leader": Chess.Leader
                }
            
            # Dynamically generates a class for each dictionary in the piecedata.py file
            for i in piecedata.piecedata:
                
                # Refmovements and newmovements are both unchanging class attributes used to determine the instance movements
                piece_type = type(i['name'], (self.role_to_class[i['role']],), {
                    'value': i['value'],
                    'promotion': i['promotion'],
                    'refmovements': i['movements'],
                    'newmovements': i['newmovements'],
                })
                
                self.piece_name_to_class[f"{i['name']}"] = piece_type

            # Initializes the chess board
            self.board = Chess.Board(self)
            
        # If there is a piece that should be able to be moved at coordinate 1, attempts to nove it to coordinate 2
        def input_to_move(self, coordinates1, coordinates2):
            obj = self.board.squares[coordinates1]['piece']
            if obj == None:
                pass
            elif obj.color != self.turn or self.board.squares[coordinates2]['isActive'] == False:
                pass
            else:
                obj.attempt_move(coordinates2)

            # After each movement, when a king could be captured, checks if there is a winner
            return self.winner()

        # Returns white if there is no black king, or black if there is no white king, otherwise None
        def winner(self):
            for l in ['black', 'white']:
                if not any(isinstance(m['piece'], Chess.Leader) and m['piece'].color == l for m in self.board.squares.values()):
                    if l == 'black':
                        return 'white'
                    else:
                        return 'black'
            return None

# Test chess game ending in white victory                
'''game = Chess.Game(False, False, 91)
game.input_to_move((4, 1), (4, 3))
game.input_to_move((3, 6), (3, 4))
game.input_to_move((4, 3), (3, 4))
game.input_to_move((4, 7), (3, 6))
game.input_to_move((4, 0), (4, 1))
game.input_to_move((3, 6), (4, 5))
print(game.input_to_move((3, 4), (4, 5)))'''