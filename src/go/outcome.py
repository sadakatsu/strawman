#!/usr/bin/env python3

from enum import auto, Enum
from math import isclose
from .color import Color


class Outcome:
    @property
    def over(self) -> bool:
        raise NotImplementedError()

    @property
    def black_points_on_board(self) -> int:
        raise NotImplementedError()

    @property
    def black_score(self) -> float:
        raise NotImplementedError()

    @property
    def white_points_on_board(self) -> int:
        raise NotImplementedError()

    @property
    def white_score(self) -> float:
        raise NotImplementedError()

    @property
    def margin(self) -> float:
        raise NotImplementedError()

    @property
    def winner(self) -> Color:
        raise NotImplementedError()


class CompleteButNotScored(Outcome, Enum):
    INSTANCE = auto()

    @property
    def over(self) -> bool:
        return True

    @property
    def black_points_on_board(self) -> int:
        return None

    @property
    def black_score(self) -> float:
        return None

    @property
    def white_points_on_board(self) -> int:
        return None

    @property
    def white_score(self) -> float:
        return None

    @property
    def margin(self) -> float:
        return None

    @property
    def winner(self) -> Color:
        return None

    def __str__(self):
        return 'Complete but not Scored'


class Draw(Outcome):
    def __init__(
        self,
        black_points_on_board: int,
        black_score: float,
        white_points_on_board: int,
        white_score: float
    ):
        self._black_points_on_board = black_points_on_board
        self._black_score = black_score
        self._white_points_on_board = white_points_on_board
        self._white_score = white_score

    @property
    def over(self) -> bool:
        return True

    @property
    def black_points_on_board(self) -> int:
        return self._black_points_on_board

    @property
    def black_score(self) -> float:
        return self._black_score

    @property
    def white_points_on_board(self) -> int:
        return self._white_points_on_board

    @property
    def white_score(self) -> float:
        return self._white_score

    @property
    def margin(self) -> float:
        return 0.

    @property
    def winner(self) -> Color:
        return None

    def __str__(self):
        return 'Draw'


class InProgress(Outcome, Enum):
    INSTANCE = auto()

    @property
    def over(self) -> bool:
        return False

    @property
    def black_points_on_board(self) -> int:
        return None

    @property
    def black_score(self) -> float:
        return None

    @property
    def white_points_on_board(self) -> int:
        return None

    @property
    def white_score(self) -> float:
        return None

    @property
    def margin(self) -> float:
        return None

    @property
    def winner(self) -> Color:
        return None

    def __str__(self):
        return 'In Progress'


class Invalidated(Outcome, Enum):
    INSTANCE = auto()

    @property
    def over(self) -> bool:
        return True

    @property
    def black_points_on_board(self) -> int:
        return None

    @property
    def black_score(self) -> float:
        return None

    @property
    def white_points_on_board(self) -> int:
        return None

    @property
    def white_score(self) -> float:
        return None

    @property
    def margin(self) -> float:
        return None

    @property
    def winner(self) -> Color:
        return None

    def __str__(self):
        return 'Invalidated'


class Win(Outcome):
    def __init__(
        self,
        black_points_on_board: int,
        black_score: float,
        white_points_on_board: int,
        white_score: float
    ):
        self._black_points_on_board = black_points_on_board
        self._black_score = black_score
        self._white_points_on_board = white_points_on_board
        self._white_score = white_score
        self._margin = abs(black_score - white_score)
        self._winner = Color.BLACK if black_score > white_score else Color.WHITE

    @property
    def over(self) -> bool:
        return True

    @property
    def black_points_on_board(self) -> int:
        return self._black_points_on_board

    @property
    def black_score(self) -> float:
        return self._black_score

    @property
    def white_points_on_board(self) -> int:
        return self._white_points_on_board

    @property
    def white_score(self) -> float:
        return self._white_score

    @property
    def margin(self) -> float:
        return self._margin

    @property
    def winner(self) -> Color:
        return self._winner

    def __str__(self):
        winner = 'Black' if self._winner is Color.BLACK else 'White'
        return f'{winner} won by {self._margin} points'


def calculate_outcome(
    black_points_on_board: int,
    black_point_adjustment: float,
    white_points_on_board: int,
    white_point_adjustment: float,
):
    final_black = black_points_on_board + black_point_adjustment
    final_white = white_points_on_board + white_point_adjustment

    if isclose(final_black, final_white):
        outcome = Draw(black_points_on_board, final_black, white_points_on_board, final_white)
    else:
        outcome = Win(black_points_on_board, final_black, white_points_on_board, final_white)
    return outcome
