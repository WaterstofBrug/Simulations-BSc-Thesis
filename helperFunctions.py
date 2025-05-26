from constants import *

def state_max(l, player):
    """ max function with ordering =<_{player} """
    if player in l:
        return player
    if T in l:
        return T
    return O if player == X else X

def replace(iter, index, value):
    if isinstance(iter, tuple):
        return iter[:index] + (value,) + iter[index+1:] 
    if isinstance(iter, list):
        return iter[:index] + [value] + iter[index+1:] 
    else:
        raise Exception ("Can only replace types list and tuples")