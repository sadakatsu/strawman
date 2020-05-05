#!/usr/bin/env python3

from typing import Iterable
from . import constants
from .board import Board
from .coordinate import *
from .outcome import *
from .pointset import PointSet
# from .rules import * # I might support multiple rule sets some day.


class Game:
    def __init__(
        self,
        # initial construction arguments
        # rules: RuleSet = None,
        span: int = 0,
        compensation: float = 0,
        handicap_placement: Iterable[Coordinate] = None,
        # game extension arguments
        source=None,
        move: Coordinate = None,
        additional_captures: int = 0,
        board: Board = None,
        outcome: Outcome = InProgress.INSTANCE,
        # game ending arguments
        dead_black_stones: int = 0,
        dead_white_stones: int = 0
    ):
        assert (
            (1 <= span <= constants.MAX_SPAN) or
            (
                isinstance(source, Game) and
                board and
                outcome and (
                    not outcome.over or dead_black_stones >= 0 and dead_white_stones >= 0
                )
            )
        )
        if span:
            self.board = Board(span=span)
            self.captures_by_black = 0
            self.captures_by_white = 0
            self.compensation = compensation
            self.current_player = Color.BLACK if not handicap_placement else Color.WHITE
            self.handicap_stones = set(handicap_placement) if handicap_placement else set()
            self.moves_played = 0
            self.outcome = InProgress.INSTANCE
            self.previous_move = None
            self.previous_state = None
            # self.rules = rules

            self.history = {
                self.board.position: [self.board]
            }

            for coordinate in self.handicap_stones:
                self.board[coordinate] = Color.BLACK
        elif outcome.over and outcome.margin is not None:
            self.board = board
            self.captures_by_black = source.captures_by_black + dead_black_stones
            self.captures_by_white = source.captures_by_white + dead_white_stones
            self.compensation = source.compensation
            self.current_player = source.current_player
            self.handicap_stones = source.handicap_stones
            self.moves_played = source.moves_played
            self.outcome = outcome
            self.history = source.history
            self.previous_move = source.previous_move
            self.previous_state = source
        else:
            self.board = board
            self.captures_by_black = source.captures_by_black
            self.captures_by_white = source.captures_by_white
            self.compensation = source.compensation
            self.current_player = source.current_player.inverse if not outcome.over else None
            self.handicap_stones = source.handicap_stones
            self.moves_played = source.moves_played + 1
            self.outcome = outcome
            self.previous_move = move
            self.previous_state = source

            if additional_captures:
                if source.current_player is Color.BLACK:
                    self.captures_by_black += additional_captures
                else:
                    self.captures_by_white += additional_captures

            if move is PASS:
                self.history = source.history
            else:
                self.history = {k: v for k, v in source.history.items()}
                position_hash = board.position
                if board.position in self.history:
                    self.history[position_hash] = (board, source.history[board.position])
                else:
                    self.history[position_hash] = (board, None)

        if self.outcome.over:
            self._legal_moves = frozenset()
        else:
            legal_moves = [coordinate for coordinate, color in self.board if color is Color.EMPTY]
            legal_moves.append(PASS)
            self.legal_moves = frozenset(legal_moves)

        self._groups, self._group_map = PointSet.sets(self.board)

    @property
    def over(self):
        return self.outcome.over

    @property
    def pass_ends_game(self):
        return self.outcome is InProgress.INSTANCE and self.previous_move is PASS

    @property
    def handicap(self):
        return len(self.handicap_stones) if self.handicap_stones else 0

    def __getitem__(self, coordinate: Coordinate):
        return self._group_map[coordinate]

    @property
    def groups(self):
        return set([group for group in self._groups if not group.color.counts_as_liberty])

    @property
    def point_sets(self):
        return set(self._groups)

    def play(self, move: Coordinate):
        self._validate_move(move)
        return self._move_pass() if move == PASS else self._move_board(move)

    def _validate_move(self, move: Coordinate):
        if self.outcome is not InProgress.INSTANCE:
            raise Exception("This Game is over; no further moves may be made (including passes).")
        elif not move == PASS:
            if move not in self.board.coordinates:
                raise Exception(f"{move} is not on this Game's Board.")
            elif self.board[move] is not Color.EMPTY:
                raise Exception(f"{move} is not playable.")

    def _move_pass(self):
        return self._pass_but_continue() if self.previous_move != PASS else self._pass_and_end()

    def _pass_but_continue(self):
        next_board = self._prepare(self.board)
        return Game(source=self, move=PASS, additional_captures=0, board=next_board, outcome=InProgress.INSTANCE)

    def _prepare(self, board: Board):
        next_board = Board(source=board)
        next_player = self.current_player.inverse
        for coordinate, color in board:
            if color.counts_as_liberty:
                playable = True
                scratch_pad = Board(source=board)
                scratch_pad[coordinate] = next_player
                captures = Game._remove_captures(scratch_pad, coordinate, next_player)
                if not captures:
                    group = PointSet(scratch_pad, coordinate)
                    if not group.reaches[Color.EMPTY]:
                        playable = False
                if playable and scratch_pad.position in self.history:
                    cons = self.history[scratch_pad.position]
                    while playable and cons:
                        playable = scratch_pad != cons[0]
                        cons = cons[1]
                next_color = Color.EMPTY if playable else Color.UNPLAYABLE
                next_board[coordinate] = next_color
        return next_board

    @staticmethod
    def _remove_captures(board: Board, start: Coordinate, played_by: Color):
        captures = 0
        other = played_by.inverse
        for coordinate in start.neighbors:
            color = board[coordinate]
            if color is other:
                group = PointSet(board, coordinate)
                if not group.reaches[Color.EMPTY]:
                    captures += len(group)
                    for member in group.members:
                        board[member] = Color.EMPTY
        return captures

    def _pass_and_end(self):
        return Game(
            source=self,
            move=PASS,
            additional_captures=0,
            board=self.board,
            outcome=CompleteButNotScored.INSTANCE
        )

    def _move_board(self, move: Coordinate):
        next_board = Board(source=self.board)
        next_board[move] = self.current_player
        additional_captures = Game._remove_captures(next_board, move, self.current_player)
        next_board = self._prepare(next_board)
        return Game(
            source=self,
            move=move,
            additional_captures=additional_captures,
            board=next_board,
            outcome=InProgress.INSTANCE
        )

    def score(self, dead_groups: Iterable[PointSet] = None):
        if self.outcome is not CompleteButNotScored.INSTANCE:
            raise Exception('score() may only be called on games that are complete but not scored.')
        dead_black_stones = 0
        dead_white_stones = 0
        clean = Board(source=self.board)
        if dead_groups:
            for group in dead_groups:
                count = len(group)
                if group.color is Color.BLACK:
                    dead_black_stones += count
                elif group.color is Color.WHITE:
                    dead_white_stones += count
                for coordinate in group:
                    clean[coordinate] = Color.EMPTY
        for coordinate, color in clean:
            if color is Color.UNPLAYABLE:
                clean[coordinate] = Color.EMPTY
        black_points_on_board = 0
        black_adjustment = abs(self.compensation) if self.compensation < 0 else 0
        white_points_on_board = 0
        white_adjustment = self.compensation if self.compensation else 0
        clean_groups, _ = PointSet.sets(clean)
        for group in clean_groups:
            points = len(group)
            if (
                group.color is Color.BLACK or
                group.color is Color.EMPTY and
                    group.reaches[Color.BLACK] and
                    not group.reaches[Color.WHITE]
            ):
                black_points_on_board += points
            elif (
                group.color is Color.WHITE or
                group.color is Color.EMPTY and
                    group.reaches[Color.WHITE] and
                    not group.reaches[Color.BLACK]
            ):
                white_points_on_board += points
        final_outcome = calculate_outcome(
            black_points_on_board,
            black_adjustment,
            white_points_on_board,
            white_adjustment
        )
        return Game(
            source=self,
            board=clean,
            dead_black_stones=dead_black_stones,
            dead_white_stones=dead_white_stones,
            outcome=final_outcome
        )

    def resume(self):
        if self.outcome is not CompleteButNotScored.INSTANCE:
            raise Exception('Only a Game that is complete but not score can be resumed.')
        return self.previous_state.previous_state

    def __str__(self):
        representation = f'{self.board.span}x{self.board.span} Game {self.outcome}, {self.moves_played} Moves'
        if not self.over:
            player = Game._represent_player(self.current_player)
            representation += f', {player} to Play'
        representation += f'\nCompensation {self.compensation}'
        if self.handicap_stones:
            handicap_representation = ', '.join(sorted(map(self._represent_coordinate, self.handicap_stones)))
            representation += f'{self.handicap}-Stone Handicap ({handicap_representation})'
        representation += f'\nBlack Captures: {self.captures_by_black}, White Captures: {self.captures_by_white}\n'
        if not self.over:
            if self.previous_move:
                previous_player = Game._represent_player(self.previous_state.current_player)
                if self.previous_move is PASS:
                    representation += f'{previous_player} passed.\n'
                else:
                    move = self._represent_coordinate(self.previous_move)
                    representation += f'{previous_player} played {move}'
                    if self.current_player is Color.BLACK:
                        captures = self.captures_by_white - self.previous_state.captures_by_white
                    else:
                        captures = self.captures_by_black - self.previous_state.captures_by_black
                    if captures:
                        representation += f', capturing {captures} stone'
                        if captures > 1:
                            representation += 's'
                    representation += '.\n'
            else:
                representation += 'Game Start\n'
        representation += '\n' + str(self.board)
        return representation

    @staticmethod
    def _represent_player(player):
        return 'Black' if player is Color.BLACK else 'White'

    def _represent_coordinate(self, coordinate):
        labels = 'ABCDEFGHJKLMNOPQRST'
        adjusted_row = self.board.span - coordinate.row + 1
        adjusted_column = labels[coordinate.column - 1]
        return f'{adjusted_column}{adjusted_row}'
