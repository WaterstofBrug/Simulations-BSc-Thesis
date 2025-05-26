from collections import Counter
from functools import reduce
from itertools import permutations, product
from math import ceil, floor, sqrt
from random import random, choice
from ClassicalBoard import Board
from QuantumBoard import QuBoard
from constants import *
from helperFunctions import *
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import Dict, Set
from strategy import *
import numpy as np
from tqdm import tqdm


def categorize_boards():
    # In this function all possible Tic tac toe boards are categorized in the set B_X, B_O, B_T and C
    recorded_boards: Dict[tuple[int], int] = {}  # dictionary; key: board (tuple repr), value win-state X,O,T

    # For each number of moves left determine for all board their win-state. This allows for determining win-state
    # in an inductive manner.
    for num_moves_left in range(10):
        # set of all possible boards made with the correct number of moves
        all_board_permutations = set(permutations([2]*ceil((9-num_moves_left)/2) + [1]*floor(((9-num_moves_left)/2)) + [0]*num_moves_left))

        for board in all_board_permutations:
            if not Board.is_valid(board):
                continue

            num_winners, winner = Board.has_winner(board)
            if num_moves_left == 0:  # this is a filled board
                # no more moves can be made, so the win-state is determined by winner
                recorded_boards[board] = winner
            elif num_winners == 1:  # there is a premature winner
                recorded_boards[board] = winner
            else:  
                board_obj = Board(board)  # make a board class version of the board tuple
                player_to_move = board_obj.player_to_move()
                preferred_win_state = O if player_to_move == X else X

                possible_moves = board_obj.get_next_boards()
                for move in possible_moves:
                    # update the best recorded win-state
                    preferred_win_state = state_max([preferred_win_state, recorded_boards[move]], player_to_move)
                
                recorded_boards[board] = preferred_win_state

    # categorizing the following sets by their recorded win-states
    B_X: Set[tuple[int]] = set(filter(lambda x: recorded_boards[x] == X, recorded_boards))
    B_O: Set[tuple[int]] = set(filter(lambda x: recorded_boards[x] == O, recorded_boards))
    B_T: Set[tuple[int]] = set(filter(lambda x: recorded_boards[x] == T, recorded_boards))
    
    C: Dict[tuple[int], Set[tuple[int]]] = dict()  # key: board upon which a mistake can be made, value: set of boards to which a mistake can lead
    for board in B_T:
        board_obj = Board(board)
        num_moves_left = Counter(board)[0]
        player_to_move = board_obj.player_to_move()
        other_player = X if player_to_move == O else O

        possible_mistakes = set(filter(lambda x: recorded_boards[x] == other_player, board_obj.get_next_boards()))
        for mistake in possible_mistakes:
            if board in C.keys():
                C[board].add(mistake)
            else:
                C[board] = {mistake}
    
    return B_T, B_X, B_O, C


def evaluate(quboard: QuBoard):
    # measure the final super position
    board = quboard.measure()

    # determine the winner
    w_n, w = Board.has_winner(board.get_board())
    if w_n == 1:
        return w
    return T


def visualize(results):
    # plotting the results
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

    for i, m_val in enumerate([O, X]):
        ax = axs[i]
        data_by_strategy = {}

        # Group data by strategy_pair for given M
        for (strategy_pair, M, prob), score_dict in results.items():
            if M != m_val:
                continue
            if strategy_pair not in data_by_strategy:
                data_by_strategy[strategy_pair] = []
            data_by_strategy[strategy_pair].append((prob, score_dict[T][0]))

        # sync colors
        strategies = set(map(lambda x: str(x), data_by_strategy.keys()))
        cmap = plt.get_cmap('Set1', len(strategies))
        colors = {strat: cmap(i) for i, strat in enumerate(strategies)}

        for strategy_pair, data in data_by_strategy.items():
            data.sort()  # sort by prob
            probs = [prob for prob, _ in data]
            means = np.array([results[(strategy_pair, m_val, prob)][T][0] for prob in probs])
            stds = np.array([results[(strategy_pair, m_val, prob)][T][1] for prob in probs])

            # Plot mean line
            ax.plot(probs, means, color=colors[str(strategy_pair)], label=str(strategy_pair))

            # Plot shaded area for mean ± std
            ax.fill_between(probs, means - stds, means + stds, color=colors[str(strategy_pair)], alpha=0.3)
        
        ax.set_title(f"Player with Mistakes plays {'X' if m_val == O else 'O'}")
        ax.set_xlabel("Probability of Making Mistakes")
        if i == 0:
            ax.set_ylabel("Number of Ties")
        ax.legend(loc="upper right")
        ax.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    # simulation specification
    num_runs = 5
    iterations = 350
    delta = 0.01
    p = [delta*i for i in range(0, int(1/delta)+1)]

    # Categorize all the boards in the sets B_X, B_O, B_T and E
    B_T, B_X, B_O, E = categorize_boards()
    print(f"|B_X| = {len(B_X)}, |B_O| = {len(B_O)}, |B_T| = {len(B_T)}, |E| = {len(E)}")

    # Initialize Strategies
    classical_without_mistakes = ClassicalWithoutMistakes(B_X, B_O, B_T, E)
    classical_with_mistakes = ClassicalWithMistakes(B_X, B_O, B_T, E)
    quantum_equal_superposition = QuantumEqualSuperposition(B_X, B_O, B_T, E)
    quantum_with_end_amplification = QuantumEndAmplification(B_X, B_O, B_T, E)
    quantum_with_full_amplification = QuantumFullAmplification(B_X, B_O, B_T, E)

    # play game with certain strategy pairings
    strategy_pairs = [
        (classical_without_mistakes, classical_with_mistakes),
        (quantum_equal_superposition, classical_with_mistakes),
        (quantum_with_end_amplification, classical_with_mistakes),
        (quantum_with_full_amplification, classical_with_mistakes),
    ]

    results_list = []

    for _ in range(num_runs):
        results = dict()

        total = len(strategy_pairs) * 2 * len(p) * iterations
        for strategy_pair, M, prob, i in tqdm(product(strategy_pairs, [X, O], p, range(iterations)), total=total, desc="Running simulations..."):
            # we iterate over the strategy pairs, the player order, prob of making a mistake, all [iterations] number of times.
            if i == 0:
                results[(strategy_pair, M, prob)] = {X: 0, O: 0, T: 0}
            
            board = QuBoard()
            prior_mappings = dict()

            # updating strategy variables
            classical_with_mistakes.set_mistake_prob(p=prob)
            for move in range(10):
                board, prior_mappings = strategy_pair[(move + M) % 2].next_move(board, prior_mappings, move)

            winner = evaluate(board)
            results[(strategy_pair, M, prob)][winner] += 1

        results_list.append(results)

    combined_results = dict()
    all_keys = set()
    for result in results_list:
        all_keys.update(result.keys())
    for key in all_keys:
        print(key)
        combined_results[key] = {M: (np.mean([results[key][M] for results in results_list]), 
                                     np.std([results[key][M] for results in results_list])) for M in [X, O, T]}

    visualize(combined_results)
    
if __name__ == "__main__":
    main()