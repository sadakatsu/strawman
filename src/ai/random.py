#!/usr/bin/env python3

from random import choice
from .agent import Agent
from go.game import Game


class RandomAgent(Agent):
    def select_move(self, game: Game):
        return choice([*game.legal_moves])
