#!/usr/bin/python3

from enum import Enum
from typing import Optional
import numpy as np


class State():
    winner: Optional[int]

    def __init__(self, board, winner):
        # A 3 x 3 uint8 numpy array with the current board state:
        # - 0 indicates empty space
        # In tic-tac-toe:
        # - 1 indicates a P1 move (X)
        # - 2 indicates a P2 move (O)
        # In dot-cross-box:
        # - 1 indicates a dot
        # - 2 indicates a cross
        # - 3 indicates a box
        self.board = board
        # Who can force a win from this state (in a optimal game):
        # 0 indicates a draw, 1 a P1 win, 2 a P2 win
        self.winner = winner
        # A list of State objects whose board states are one move away from the
        # current one
        self.children = []


class Solver():

    def __init__(self):
        self.Variant = Enum('Variant', ['TIC_TAC_TOE', 'DOT_CROSS_BOX'])
        self.variant = self.Variant.DOT_CROSS_BOX
        self.start_state = None
        # key: board state bytes, val: corresponding State object
        self.solved = {}
        # Total number of board states to solve
        self.total = 5478 if self.variant == self.Variant.TIC_TAC_TOE else 206556

    def solve(self):
        self.start_state = self.explore(np.zeros((3, 3), dtype='uint8'), 1)
        print('\nFinished solving.')

    def explore(self, board, turn):
        # Test if board has been solved already
        board_key = board.tobytes()
        if board_key in self.solved:
            return self.solved[board_key]
        # Otherwise, make a new state
        state = State(board, None)
        self.solved[board.tobytes()] = state
        print(f'Solving board state {len(self.solved)}/{self.total}.', end='\r')
        # Test is game is over at this state
        state.winner = self.is_finished(board)
        if state.winner is not None:
            return state
        # Otherwise, explore next board
        next_turn = (turn % 2) + 1
        can_win = False
        can_draw = False
        # For each of the nine positions...
        for r in range(3):
            for c in range(3):
                child_board = board.copy()
                if self.variant == self.Variant.TIC_TAC_TOE:
                    # In normal tic-tac-toe, a move is valid if the space is
                    # empty (0)
                    if child_board[r, c] > 0:
                        continue
                    child_board[r, c] = turn
                else:
                    # In the dot-cross-box variant, a move is valid if the
                    # space is empty (0), a dot (1), or a cross (2)
                    if child_board[r, c] > 2:
                        continue
                    child_board[r, c] += 1
                # If the move is valid, explore it
                child = self.explore(child_board, next_turn)
                state.children.append(child)
                if child.winner == turn:
                    can_win = True
                elif child.winner == 0:
                    can_draw = True
        # In an optimal game:
        #   1. This player will be able to win
        if can_win:
            state.winner = turn
        #   2. This player can manage a draw (but not a win)
        elif can_draw:
            state.winner = 0
        #   3. This player will lose
        else:
            state.winner = next_turn
        return state

    def is_finished(self, board):
        # Get arrays with each of the eight groups of three (3 rows, 3 cols, 2
        # diagonals)
        groups = ([row for row in board] + [col for col in board.T] +
                  [board[(0, 1, 2), (0, 1, 2)], board[(0, 1, 2), (2, 1, 0)]])
        if self.variant == self.Variant.TIC_TAC_TOE:
            # Test for P1/P2 win
            for group in groups:
                if np.all(group == 1):
                    return 1
                if np.all(group == 2):
                    return 2
            # Test for draw (the whole board is filled)
            if np.all(board > 0):
                return 0
            return None
        else: # Dot-cross-box
            # Test for draw (group of three 3s)
            for group in groups:
                if np.all(group == 3):
                    return 0
            # Test for P1 win (group of three 1s or three 2s)
            for group in groups:
                if np.all(group == 1) or np.all(group == 2):
                    return 1
            # Test for P2 win (three 3s, not in a group)
            if np.sum(board == 3) > 2:
                return 2


if __name__ == '__main__':
    solver = Solver();
    solver.solve();
