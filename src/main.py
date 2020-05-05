#!/usr/bin/env python3

import random
from go.color import Color
from go.coordinate import Coordinate, Coordinates, get_coordinates
from go.game import Game
from go.outcome import Draw
from ai.agent import Agent
from ai.naive import NaiveAgent
from ai.random import RandomAgent


def _play_match(weaker: Agent, stronger: Agent, handicap: int, print_updates=False):
    players = {Color.BLACK: weaker, Color.WHITE: stronger}
    if handicap:
        compensation = -7
        if handicap > 1:
            coordinates = get_coordinates(9)
            handicap_stones = [coordinates.get(7, 3), coordinates.get(3, 7)]
            if handicap > 2:
                handicap_stones.append(coordinates.get(7, 7))
            if handicap > 3:
                handicap_stones.append(coordinates.get(3, 3))
            if handicap in (5, 7, 9):
                handicap_stones.append(coordinates.get(5, 5))
            if handicap > 5:
                handicap_stones.append(coordinates.get(3, 5))
                handicap_stones.append(coordinates.get(7, 5))
            if handicap > 7:
                handicap_stones.append(coordinates.get(5, 3))
                handicap_stones.append(coordinates.get(5, 7))
        else:
            handicap_stones = None
    else:
        compensation = 7
        handicap_stones = None
    game = Game(span=9, compensation=compensation, handicap_placement=handicap_stones)
    while not game.over:
        if print_updates:
            print(game)
        agent = players[game.current_player]
        move = agent.select_move(game)
        game = game.play(move)
    if print_updates:
        print(game)
    game = game.score()
    if print_updates:
        print(game)
    return game.outcome


if __name__ == '__main__':
    naive_agent = NaiveAgent()
    random_agent = RandomAgent()
    _play_match(naive_agent, random_agent, 0, True)

    for handicap in range(-9, 10):
        results = [0, 0, 0]
        for match in range(100):
            if handicap < 0 or handicap == 0 and handicap % 2 == 0:
                weaker = naive_agent
                stronger = random_agent
                color = Color.BLACK
            else:
                weaker = random_agent
                stronger = naive_agent
                color = Color.WHITE
            outcome = _play_match(weaker, stronger, abs(handicap))
            if isinstance(outcome, Draw):
                results[1] += 1
            elif outcome.winner is color:
                results[0] += 1
            else:
                results[2] += 1
        print(handicap, results)
