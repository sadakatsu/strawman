#!/usr/bin/env python3

from .color import Color
from .coordinate import get_coordinates, Coordinate
from .constants import *
import random


def _generate_hash():
    return random.getrandbits(ZOBRIST_HASH_SIZE)


def _create_coordinate_state_hashes():
    cache = {}
    for coordinate in get_coordinates(MAX_SPAN):
        for color in Color:
            zobrist_hash = _generate_hash()
            cache[(coordinate, color)] = zobrist_hash
    return cache


_COORDINATES = _create_coordinate_state_hashes()


def get_cell_hash(coordinate, color: Color):
    return _COORDINATES[(coordinate, color)]


_EMPTY_BOARDS = {}


def get_empty_board(span: int):
    assert 1 <= span <= MAX_SPAN
    if span not in _EMPTY_BOARDS:
        empty_hash = 0
        for coordinate in get_coordinates(span):
            empty_hash ^= get_cell_hash(coordinate, Color.EMPTY)
        _EMPTY_BOARDS[span] = empty_hash
    return _EMPTY_BOARDS[span]


BLACK_TO_PLAY = _generate_hash()
GAME_OVER = _generate_hash()
WHITE_TO_PLAY = _generate_hash()

PREVIOUS_MOVE_PLAY = _generate_hash()
PREVIOUS_MOVE_FIRST_PASS = _generate_hash()
PREVIOUS_MOVE_SECOND_PASS = _generate_hash()
