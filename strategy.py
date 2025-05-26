from abc import ABC, abstractmethod
from ClassicalBoard import Board
from QuantumBoard import QuBoard
from constants import *
from helperFunctions import *
from random import random, choice

class Strategy(ABC):
    def __init__(self, B_X, B_O, B_T, E):
        self.B_X = B_X
        self.B_O = B_O
        self.B_T = B_T
        self.E = E

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    
    @abstractmethod
    def next_move(self, board, prior_mappings, move):
        pass

class ClassicalStrategy(Strategy):
    def __init__(self, *args):
        return super().__init__(*args)

    def next_move(self, quboard, prior_mappings, move):
        if move == 9:
            return quboard, prior_mappings

        decomposition = {}
        for board in quboard.get_decomp().keys():
            # classically determine next move
            next_board, prior_mappings = self.classical_next_move(Board(board), prior_mappings)
            next_board = next_board.get_board()  # get board since quantum decomp must work on tuples 

            # add the new move in a decomposition
            if next_board in decomposition.keys():
                decomposition[next_board] = decomposition[next_board] + quboard.get_decomp()[board]
            else:
                decomposition[next_board] = quboard.get_decomp()[board]
        
        return QuBoard(decomposition), prior_mappings
    
    @abstractmethod
    def classical_next_move(self, board: Board, prior_mappings):
        pass


class ClassicalWithoutMistakes(ClassicalStrategy):
    def classical_next_move(self, board, prior_mappings):
        """ This function chooses a board following the most optimal classical strategy """ 
        if board in prior_mappings.keys():
            return prior_mappings[board]

        type = T
        if board.get_board() in self.B_X:
            type = X
        elif board.get_board() in self.B_O:
            type = O 

        possible_next_moves = list(filter(lambda x: (type == T and x in self.B_T) 
                                          or (type == X and x in self.B_X) 
                                          or (type == O and x in self.B_O), board.get_next_boards()))
        
        if not possible_next_moves:
            print(board.get_board(), board.get_board() in self.B_T, board.get_board() in self.B_O, 
                  board.get_board() in self.B_T, type, board.get_next_boards())
            raise Exception ("no next moves")

        next_move = choice(possible_next_moves)
        prior_mappings[board] = Board(next_move)

        return Board(next_move), prior_mappings
    
class ClassicalWithMistakes(ClassicalStrategy):
    def __init__(self, *args):
        self.mistake_prob = 0
        self.no_mistakes_strategy = ClassicalWithoutMistakes(*args)
        super().__init__(*args)

    def classical_next_move(self, board: Board, prior_mappings):
        if board in prior_mappings.keys():  # ensure prior mistakes are repeated 
            return prior_mappings[board]
        
        if board.get_board() in self.E.keys() and random() < self.mistake_prob:  # we may make a mistake now
            new_move = choice(list(self.E[board.get_board()]))
            prior_mappings[board] = Board(new_move)
            return Board(new_move), prior_mappings
        
        # we will make no mistake
        return self.no_mistakes_strategy.classical_next_move(board, prior_mappings)
    
    def set_mistake_prob(self, p):
        if not 0 <= p <= 1:
            raise Exception (f"Invalid Probability {p}")
        
        self.mistake_prob = p

class QuantumEqualSuperposition(Strategy):
    def next_move(self, quboard, prior_mappings, move):
        if move == 9:
            return quboard, prior_mappings
        
        decomposition = {}
        for board in quboard.get_decomp().keys():
            # generate all possible moves 
            next_boards = Board(board).get_next_boards()

            # filter the moves to only good moves
            win_class = self.B_X if board in self.B_X else (self.B_O if board in self.B_O else self.B_T)  # determine the win-state set in which the board resides
            next_boards = set(filter(lambda x: x in win_class, next_boards)) 

            # create a new decomposition of all possible good moves
            for next_board in next_boards:
                if next_board in decomposition.keys():
                    decomposition[next_board] = decomposition[next_board] + quboard.get_decomp()[board] * 1/len(next_boards)
                else:
                    decomposition[next_board] = quboard.get_decomp()[board] * 1/len(next_boards)

        return QuBoard(decomposition), prior_mappings
    
class QuantumEndAmplification(QuantumEqualSuperposition):
    def next_move(self, board, prior_mappings, move):
        player = X if move % 2 == 0 else O

        board, prior_mappings = super().next_move(board, prior_mappings, move)

        if move == 8 or move == 9:
            board.amplify(self.B_X if player == X else self.B_O)

        return board, prior_mappings
    
class QuantumFullAmplification(QuantumEqualSuperposition):
    def next_move(self, board, prior_mappings, move):
        player = X if move % 2 == 0 else O

        board, prior_mappings = super().next_move(board, prior_mappings, move)
        
        board.amplify(self.B_X if player == X else self.B_O)

        return board, prior_mappings
    