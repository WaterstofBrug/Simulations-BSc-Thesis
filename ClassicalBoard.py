from collections import Counter
from functools import reduce
from itertools import permutations
from math import ceil, floor, sqrt
from random import random, choice
from constants import *
from helperFunctions import *

class Board:
    def __init__(self, board=None):
        self.__board = tuple((EMPTY for _ in range(SIZE)))

        if board is not None:
            self.set_board(board)

    def __repr__(self):
        return ''.join(map(str, self.__board))

    def get_board(self):
        return self.__board
    
    def is_full(self):
        return EMPTY not in self.__board
    
    def set_board(self, board):
        if Board.is_valid(board):
            self.__board = board
        else:
            raise Exception("Invalid board")

    def player_to_move(self):
        markings = Counter(self.__board)
        return O if markings[EMPTY] % 2 == 0 else X

    def get_next_boards(self):
        """ Returns a set of valid boards which follow self.__board"""
        player_to_move = self.player_to_move()
        possible_moves = set()
        
        w_n, _ = Board.has_winner(self.__board)
        if w_n == 1:
            return {self.__board} 

        for i, field in enumerate(self.__board):
            if field != EMPTY:
                continue
            # field is empty

            possible_next_move = replace(self.__board, i, player_to_move)
            if Board.is_valid(possible_next_move):
                # possible move is a valid move
                possible_moves.add(possible_next_move)
        
        return possible_moves


    @staticmethod
    def is_valid(board: tuple[int]):
        # correct shape
        corr_shape = len(board) == SIZE
        if not corr_shape:
            return False

        # correct markings, EMPTY, X, O
        markings = Counter(board)
        corr_markings = reduce(lambda x, y: x in [EMPTY, X, O] and y in [EMPTY, X, O], markings.keys()) or list(markings.keys()) == [0]

        # number of winners <= 1
        number_of_winners, winner = Board.has_winner(board)
        corr_n_winners = number_of_winners <= 1

        # correct number of X's and O's
        corr_n_markings = (0 <= markings[X] - markings[O] <= 1 and number_of_winners == 0) \
                    or (number_of_winners == 1 and winner == X and markings[X] == markings[O] + 1) \
                    or (number_of_winners == 1 and winner == O and markings[X] == markings[O])

        return corr_shape and corr_markings and corr_n_winners and corr_n_markings 
    
    @staticmethod
    def has_winner(board: list[int]) -> tuple[int, int]:
        """
        This function will return the numbers of winners on the board. Iff the number of winners is 1 then winner will indicate
        the player who won. If the number of winners is 0 winner will be an empty string and if the number of winners is 2
        winner will be arbitrary.
        """

        lines = [(i*3 + 0,i*3 + 1,i*3 + 2) for i in range(3)] + [(0+i,3+i,6+i) for i in range(3)] + [(0, 4, 8), (2, 4, 6)]

        winner = T
        number_of_winners = 0
        for line in lines:
            if board[line[0]] == board[line[1]] and board[line[1]] == board[line[2]] and board[line[2]] != EMPTY:
                # A line has the same non-empty marking
                if winner != board[line[0]] and number_of_winners < 2:
                    # if the winner is not of the marking and we do not have two markings as winners we update
                    # the marking and add one winner
                    number_of_winners += 1
                    winner = board[line[0]]

        return number_of_winners, winner