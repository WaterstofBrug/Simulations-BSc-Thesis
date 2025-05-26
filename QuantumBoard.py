from collections import Counter
from functools import reduce
from itertools import permutations
from math import ceil, floor, sqrt, sin, cos, pi
from numpy import arcsin
from random import random, choice
from constants import *
from helperFunctions import *
from ClassicalBoard import Board


class QuBoard:
    def __init__(self, decomp=None):
        self.__decomposition = {tuple((0 for _ in range(9))): 1}  # {|psi>: a_psi}
        # NOTE decomposition keys are tuples since making Board classes keys distinguishes the same states
        # by different class-pointers

        if decomp is not None:
            self.set_decomp(decomp)

    def __repr__(self):
        return " \n".join(map(lambda x : f"{x} : {round(self.__decomposition[x], 3)}...", list(self.__decomposition.keys())))

    def set_decomp(self, decomp):
        if not QuBoard.is_valid(decomp):
            print(sum(map(lambda x: x, decomp.values())))
            raise Exception ("Invalid quantum board decomposition")

        self.__decomposition = decomp
    
    def get_decomp(self):
        return self.__decomposition
    
    def is_empty(self):
        return self.__decomposition == {tuple((0 for _ in range(9))): 1}
    
    def measure(self):
        bench = random()
        sum = 0
        for board in self.__decomposition:
            sum += self.__decomposition[board]
            if sum > bench:
                # collapse to board
                self.__decomposition = {board: 1}
                return Board(board)
        
        # by floating point error no collapse happend
        print("No collapse by floating point error")
        return self.measure()
    
    def amplify(self, B_M, n=None):
        """ This method will simulate a amplitude amplification """

        good_boards = B_M & self.__decomposition.keys()

        # first determine a NOTE in this simulation coefficients are already squared and never complex
        a = sum([abs(self.__decomposition[board]) for board in good_boards])

        # we assume 0 < a < 1 otherwise amplification will have no effect (only good or only bad states)
        if a < 0.0001 or abs(a - 1) < 0.0001:
            return

        # this should be unnesecary but both of these conditions should also imply a = 0 or a = 1
        if not good_boards or len(self.__decomposition) - len(good_boards) == 0: 
            print("'a' measure went wrong?")
            return

        # determine theta following THE paper
        theta = arcsin(sqrt(a))

        if n is None:
            # No specific n specified so n will be determined
            n = floor(pi/(4*theta))

        # applying Q n times
        p_good_coeff = sin((2*n+1)*theta)**2 / a
        p_bad_coeff = cos((2*n+1)*theta)**2 / (1-a)

        #print(f"good coeff {p_good_coeff} bad coeff {p_bad_coeff}")

        for board in self.__decomposition.keys():  # multiply states with proper coefficients
            if board in B_M:
                self.__decomposition[board] *= p_good_coeff
            else:
                self.__decomposition[board] *= p_bad_coeff
        
        return



    @staticmethod
    def sum(qu_boards):
        n = len(qu_boards)
        decomp_sum = dict()

        for qu_board in qu_boards:
            decomp = qu_board.get_decomp()
            
            for board in decomp.keys():
                if board in decomp_sum.keys():  # TODO update sqrt
                    decomp_sum[board] += decomp[board] * sqrt(n)
                else:
                    decomp_sum[board] = decomp[board] * sqrt(n)

        return QuBoard(decomp_sum)

    @staticmethod
    def is_valid(q_board):
        bool = True

        for classic_board in q_board.keys():
            bool &= Board.is_valid(classic_board)
        
        return bool and abs(sum(map(lambda x: x, q_board.values())) - 1) < 0.0001
        