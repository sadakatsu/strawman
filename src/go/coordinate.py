#!/usr/bin/env python3

from .constants import MAX_SPAN
from typing import List


class Coordinate:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column
        self.neighbors: List[Coordinate] = []
        self.corners: List[Coordinate] = []
        self._hash = hash((self.row, self.column))

    def __deepcopy__(self, memodict = {}):
        return self

    def __str__(self):
        return f'{self.column:02}-{self.row:02}'

    def __eq__(self, other):
        return other is self or isinstance(other, Coordinate) and self.row == other.row and self.column == other.column

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._hash

class Coordinates:
    def __init__(self, span: int):
        assert 1 <= span <= MAX_SPAN
        self.span = span
        self._coordinates = [Coordinate(row, column) for row in range(1, span + 1) for column in range(1, span + 1)]
        for coordinate in self._coordinates:
            for pair in [
                (coordinate.row - 1, coordinate.column),
                (coordinate.row, coordinate.column - 1),
                (coordinate.row, coordinate.column + 1),
                (coordinate.row + 1, coordinate.column)
            ]:
                row, column = pair
                if self._validate_coordinate(row, column):
                    index = self._calculate_index(row, column)
                    other = self._coordinates[index]
                    coordinate.neighbors.append(self._coordinates[index])
            for pair in [
                (coordinate.row - 1, coordinate.column - 1),
                (coordinate.row - 1, coordinate.column + 1),
                (coordinate.row + 1, coordinate.column - 1),
                (coordinate.row + 1, coordinate.column + 1)
            ]:
                row, column = pair
                if self._validate_coordinate(row, column):
                    index = self._calculate_index(row, column)
                    other = self._coordinates[index]
                    coordinate.corners.append(other)

    def _validate_coordinate(self, row: int, column: int):
        return self._validate_component(row) and self._validate_component(column)

    def _validate_component(self, component):
        return 1 <= component <= self.span

    def _calculate_index(self, row: int, column: int):
        return (row - 1) * self.span + column - 1

    def get(self, row: int, column: int):
        self._validate_coordinate(row, column)
        index = self._calculate_index(row, column)
        return self._coordinates[index]

    def __iter__(self):
        return iter(self._coordinates)

    def __contains__(self, coordinate: Coordinate):
        return coordinate and self._validate_coordinate(coordinate.row, coordinate.column)


_coordinates = {}


def get_coordinates(span: int):
    assert 1 <= span <= MAX_SPAN
    if span not in _coordinates:
        _coordinates[span] = Coordinates(span)
    return _coordinates[span]


PASS = Coordinate(-1, -1)
