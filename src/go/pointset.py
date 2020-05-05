#!/usr/bin/env python3

from collections import deque
from .board import Board
from .color import Color
from .coordinate import Coordinate


class PointSet:
    @staticmethod
    def sets(board: Board):
        coordinate_to_point_set = dict()
        sets = set()
        for coordinate, _ in board:
            if coordinate not in coordinate_to_point_set:
                point_set = PointSet(board, coordinate)
                sets.add(point_set)
                for member in point_set:
                    coordinate_to_point_set[member] = point_set
        return sets, coordinate_to_point_set

    def __init__(self, board: Board, start: Coordinate):
        self.color = board[start].simple
        self.members = {start}
        self.reaches = {x: False for x in Color}
        to_visit = deque([start])
        queued = {start}
        while to_visit:
            current = to_visit.popleft()
            color = board[current].simple
            if color is self.color:
                self.members.add(current)
                for neighbor in current.neighbors:
                    if neighbor not in queued:
                        to_visit.append(neighbor)
                        queued.add(neighbor)
            else:
                self.reaches[color] = True

    def __iter__(self):
        return iter(self.members)

    def __len__(self):
        return len(self.members)
