#!/usr/bin/env python3

from go.game import Game


class Agent:
    def __init__(self):
        pass

    def select_move(self, game: Game):
        raise NotImplementedError()
