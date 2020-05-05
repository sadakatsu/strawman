#!/usr/bin/env python3

from . import constants, zobrist
from .color import Color
from .coordinate import get_coordinates, Coordinate, Coordinates


class Board:
    def __init__(
        self,
        span: int = None,
        source=None
    ):
        if source is None:
            assert span is not None and 1 <= span <= constants.MAX_SPAN
            self.coordinates = get_coordinates(span)
            self.span = span
            self.cells = {coordinate: Color.EMPTY for coordinate in self.coordinates}
            self.position = zobrist.get_empty_board(span)
        else:
            assert isinstance(source, Board)
            self.coordinates = source.coordinates
            self.span = source.span
            self.cells = {k: v for k, v in source.cells.items()}
            self.position = source.position

    def __getitem__(self, coordinate: Coordinate):
        return self.cells[coordinate]

    def __setitem__(self, coordinate: Coordinate, next_color: Color):
        current_color = self.cells[coordinate]
        if current_color != next_color:
            current_hash = zobrist.get_cell_hash(coordinate, current_color.simple)
            next_hash = zobrist.get_cell_hash(coordinate, next_color.simple)
            if current_hash != next_hash:
                self.position ^= current_hash ^ next_hash
            self.cells[coordinate] = next_color

    def __eq__(self, other):
        return (
            isinstance(other, Board) and
            self.span == other.span and
            self.position == other.position and
            self.cells == other.cells
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        representation = self._column_labels()
        for row in range(1, self.span + 1):
            top_edge = row == 1
            bottom_edge = row == self.span

            row_label = f'{self.span - row + 1:2}'
            representation += row_label + ' '

            for column in range(1, self.span + 1):
                coordinate = self.coordinates.get(row, column)
                color = self.cells[coordinate]
                if color is Color.EMPTY:
                    left_edge = column == 1
                    right_edge = column == self.span

                    if top_edge:
                        if left_edge:
                            representation += '┌'
                        elif right_edge:
                            representation += '┐'
                        else:
                            representation += '┬'
                    elif bottom_edge:
                        if left_edge:
                            representation += '└'
                        elif right_edge:
                            representation += '┘'
                        else:
                            representation += '┴'
                    elif left_edge:
                        representation += '├'
                    elif right_edge:
                        representation += '┤'
                    else:
                        representation += '┼'

                elif color is Color.BLACK:
                    representation += '●'
                elif color is Color.WHITE:
                    representation += '○'
                else:
                    representation += '∙'
            representation += f' {row_label}\n'
        representation += self._column_labels()
        return representation

    def _column_labels(self):
        return '   ' + 'ABCDEFGHJKLMNOPQRST'[:self.span] + '\n'

    def __iter__(self):
        for coordinate in self.coordinates:
            color = self[coordinate]
            yield coordinate, color

    def __contains__(self, coordinate: Coordinate):
        return coordinate in self.coordinates
