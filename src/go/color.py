#!/usr/bin/env python3

from enum import auto, Enum


class Color(Enum):
    EMPTY = (0, True,)
    BLACK = (1, False,)
    WHITE = (2, False,)
    UNPLAYABLE = (3, True,)

    def __init__(self, index, counts_as_liberty):
        self.index = index
        self.counts_as_liberty = counts_as_liberty
        self.inverse = self
        self.simple = self


Color.BLACK.inverse = Color.WHITE
Color.WHITE.inverse = Color.BLACK
Color.UNPLAYABLE.simple = Color.EMPTY
