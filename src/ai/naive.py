#!/usr/bin/env python3

from random import choice
from .agent import Agent
from go.board import Board
from go.color import Color
from go.coordinate import Coordinate
from go.game import Game, PASS

# This file's contents are shameless rewrites of the naive agent presented in _Deep Learning and the Game of Go_.  See
# https://github.com/maxpumperla/deep_learning_and_the_game_of_go .  While this agent is very weak, it provides another
# agent against which the strawman can be tested.


def _is_point_an_eye(board: Board, point: Coordinate, color: Color):
    # The point must be on the board and empty.
    if point not in board or not board[point].counts_as_liberty:
        return False
    # All adjacent points must contain friendly stones.
    for neighbor in point.neighbors:
        if board[neighbor] is not color:
            return False
    # We must control 3 out of 4 corners if the point is in the middle of the board; on the edge we must control all
    # corners.
    friendly = 0
    total = 0
    for corner in point.corners:
        total += 1
        if board[corner] is color:
            friendly += 1
    return friendly >= 3 if total == 4 else friendly == total


class NaiveAgent(Agent):
    def select_move(self, game: Game):
        candidates = [
            move
            for move in game.legal_moves
            if move != PASS and not _is_point_an_eye(game.board, move, game.current_player)
        ]
        return choice(candidates) if len(candidates) > 0 else PASS
