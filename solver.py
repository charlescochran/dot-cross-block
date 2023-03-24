#!/usr/bin/python3

from enum import Enum
import numpy as np


class Solver():

    def __init__(self):
        self.Variant = Enum('Variant', ['TIC_TAC_TOE', 'DOT_CROSS_BOX'])
        self.variant = self.Variant.DOT_CROSS_BOX
        # key: board state bytes, val: who can force a win (0 for draw, 1 for
        # p1, 2 for p2)
        self.solved = {}
        # finished games: [no. draws, no. p1 wins, no. p2 wins]
        self.winners = [0, 0, 0]
        # no. solved unique board states
        self.solve_count = 0

    def solve(self):
        start_board = np.zeros((3, 3), dtype='uint8')
        winner = self.explore(start_board, 1)
        print(f'Solved {self.solve_count} unique board states. ')
        print(f'Winner is {winner} (0 = draw, 1 = P1, 2 = P2).')
        print(f'Unique ending board states:')
        print(f'  Draws: {self.winners[0]}')
        print(f'  P1 wins: {self.winners[1]}')
        print(f'  P2 wins: {self.winners[2]}')

    def explore(self, board, turn):
        # Test if board has been solved already
        board_key = board.tobytes()
        if board_key in self.solved:
            winner = self.solved[board_key]
            return winner
        # Test is game is over
        winner = self.is_finished(board)
        if winner is not None:
            self.add_solved_board(board, winner)
            return winner
        # Otherwise, explore next boards
        next_turn = (turn % 2) + 1
        can_win = False
        can_draw = False
        # For each of the nine positions
        for r in range(3):
            for c in range(3):
                new = board.copy()
                if self.variant == self.Variant.TIC_TAC_TOE:
                    # In normal tic-tac-toe, a move is valid if the space is
                    # empty (0)
                    if new[r, c] > 0:
                        continue
                    new[r, c] = turn
                else:
                    # In the dot-cross-box variant, a move is valid if the
                    # space is empty (0), a dot (1), or a cross (2)
                    if new[r, c] > 2:
                        continue
                    new[r, c] += 1
                # If the move is valid, try it
                winner = self.explore(new, next_turn)
                if winner == turn:
                    can_win = True
                elif winner == 0:
                    can_draw = True
        # This player will be able to win
        if can_win:
            self.add_solved_board(board, turn)
            return turn
        # This player can manage a draw (but not a win)
        if can_draw:
            self.add_solved_board(board, 0)
            return 0
        # This player will definitely lose
        self.add_solved_board(board, next_turn)
        return next_turn

    def add_solved_board(self, board, winner):
        self.solve_count += 1
        # Add all rotations/reflections (8 total) of this board to the solved list.
        # Duplicates caused by symmetrical boards will simply have no effect.
        self.solved[board.tobytes()] = winner                     # current board
        self.solved[np.rot90(board).tobytes()] = winner           # 90 deg rotation
        self.solved[np.flip(board).tobytes()] = winner            # 180 deg rotation
        self.solved[np.flip(np.rot90(board)).tobytes()] = winner  # 270 deg rotation
        mirror = np.fliplr(board.copy())
        self.solved[mirror.tobytes()] = winner                    # mirror
        self.solved[np.rot90(mirror).tobytes()] = winner          # 90 deg rotation
        self.solved[np.flip(mirror).tobytes()] = winner           # 180 deg rotation
        self.solved[np.flip(np.rot90(mirror)).tobytes()] = winner # 270 deg rotation

    def is_finished(self, board):
        # Get arrays with each of the eight groups of three (3 rows, 3 cols, 2
        # diagonals)
        groups = ([row for row in board] + [col for col in board.T] +
                  [board[(0, 1, 2), (0, 1, 2)], board[(0, 1, 2), (2, 1, 0)]])
        if self.variant == self.Variant.TIC_TAC_TOE:
            # Test for P1/P2 win
            for group in groups:
                if np.all(group == 1):
                    self.winners[1] += 1
                    return 1
                if np.all(group == 2):
                    self.winners[2] += 1
                    return 2
            # Test for draw (the whole board is filled)
            if np.all(board > 0):
                self.winners[0] += 1
                return 0
            return None
        else: # Dot-cross-box
            # Test for draw (group of three 3s)
            for group in groups:
                if np.all(group == 3):
                    self.winners[0] += 1
                    return 0
            # Test for P1 win (group of three 1s or three 2s)
            for group in groups:
                if np.all(group == 1) or np.all(group == 2):
                    self.winners[1] += 1
                    return 1
            # Test for P2 win (three 3s, not in a group)
            if np.sum(board == 3) > 2:
                self.winners[2] += 1
                return 2


if __name__ == '__main__':
    solver = Solver();
    solver.solve();
