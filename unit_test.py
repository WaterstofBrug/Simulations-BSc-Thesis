import unittest
from constants import *

import ClassicalBoard
import QuantumBoard
import helperFunctions
import main

class TestClassicalBoard(unittest.TestCase):
    def test_is_valid(self):
        self.assertTrue(QuantumBoard.Board.is_valid([0,0,0,
                                                     0,0,0,
                                                     0,0,0]))
        self.assertFalse(QuantumBoard.Board.is_valid([0,0,0,
                                                      0,0,0,
                                                      0,0,0,0]))
        self.assertFalse(QuantumBoard.Board.is_valid([0,0,0,
                                                      0,0,0,
                                                      0,0]))
        self.assertFalse(QuantumBoard.Board.is_valid([0,0,0,
                                                      0,0,0,
                                                      0,0,3]))
        self.assertFalse(QuantumBoard.Board.is_valid([O,0,0,
                                                      0,0,0,
                                                      0,0,0]))
        self.assertTrue(QuantumBoard.Board.is_valid([X,0,0,
                                                     0,0,0,
                                                     0,0,0]))
        self.assertTrue(QuantumBoard.Board.is_valid([O,0,X,
                                                     X,O,O,
                                                     X,0,X]))
        self.assertTrue(QuantumBoard.Board.is_valid([O,O,X,
                                                     X,O,O,
                                                     X,X,X]))
        self.assertFalse(QuantumBoard.Board.is_valid([O,X,X,
                                                      O,O,O,
                                                      X,X,X]))
        self.assertFalse(QuantumBoard.Board.is_valid([X,X,X,
                                                      O,O,O,
                                                      0,0,0]))
        self.assertFalse(QuantumBoard.Board.is_valid([O,X,O,
                                                      O,X,O,
                                                      0,X,0]))
        self.assertFalse(QuantumBoard.Board.is_valid([O,0,X,
                                                      X,O,X,
                                                      0,X,O]))
    
    def test_has_winner(self):
        self.assertEqual(QuantumBoard.Board.has_winner([0,0,0,
                                                        0,0,0,
                                                        0,0,0])[0], 0)
        self.assertEqual(QuantumBoard.Board.has_winner([O,O,X,
                                                        0,X,0,
                                                        O,0,0])[0], 0)
        self.assertEqual(QuantumBoard.Board.has_winner([X,X,X,
                                                        O,O,X,
                                                        O,O,X]), (1, X))
        self.assertEqual(QuantumBoard.Board.has_winner([O,O,O,
                                                        X,X,X,
                                                        0,0,0])[0], 2)
        self.assertEqual(QuantumBoard.Board.has_winner([X,X,O,
                                                        O,O,X,
                                                        X,O,X]), (0, T))
        self.assertEqual(QuantumBoard.Board.has_winner([X,X,X,
                                                        O,O,0,
                                                        X,0,0]), (1, X))

class TestQuantumBoard(unittest.TestCase):
    def test_test(self):
        self.assertTrue(True)

class TestHelperFunctions(unittest.TestCase):
    def test_test(self):
        self.assertTrue(True)

class TestMainFunctions(unittest.TestCase):
    def test_test(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()