#!/usr/bin/python3

from enum import Enum
import random
from collections import deque


class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    UNPLAYABLE = 3


COLORS = [Color.EMPTY, Color.BLACK, Color.WHITE, Color.UNPLAYABLE]


def position_color(color):
    return color if color is not Color.UNPLAYABLE else Color.EMPTY


def counts_as_liberty(color):
    return color != Color.BLACK and color != Color.WHITE


def opposite(color):
    if color is Color.EMPTY or color is Color.UNPLAYABLE:
        return color
    elif color is Color.BLACK:
        return Color.WHITE
    else:
        return Color.BLACK


class Outcome:
    def __init__(
        self,
        label,
        over,
        black_points_on_board=None,
        black_score=None,
        white_points_on_board=None,
        white_score=None
    ):
        self.label = label
        self.over = over
        if self.over:
            self.blackPointsOnBoard = black_points_on_board
            self.blackScore = black_score
            self.whitePointsOnBoard = white_points_on_board
            self.whiteScore = white_score

            if black_score is not None:
                margin = black_score - white_score
                if margin == 0:
                    self.margin = 0
                    self.winner = None
                elif margin > 0:
                    self.margin = margin
                    self.winner = Color.BLACK
                else:
                    self.margin = -margin
                    self.winner = Color.WHITE
            else:
                self.margin = None
                self.winner = None

    def is_over(self):
        return self.over

    def get_black_points_on_board(self):
        return self.blackPointsOnBoard if self.over else None

    def get_black_score(self):
        return self.blackScore if self.over else None

    def get_white_points_on_board(self):
        return self.whitePointsOnBoard if self.over else None

    def get_white_score(self):
        return self.whiteScore if self.over else None

    def get_margin(self):
        return self.margin if self.over else None

    def get_winner(self):
        return self.winner if self.over else None

    def __str__(self):
        if self.over and self.margin:
            return f'{"Black" if self.winner is Color.BLACK else "White"} wins by {self.margin}'
        else:
            return self.label

    def __eq__(self, other):
        return (
            type(other) is Outcome and
            self.label == other.label and
            self.over == other.over and
            self.margin == other.margin
        )


IN_PROGRESS = Outcome('In Progress', False)
COMPLETED_BUT_NOT_SCORED = Outcome('Completed but not Scored', True)


def finish(black_points_on_board, black_score, white_points_on_board, white_score):
    label = 'Draw' if black_score == white_score else 'Win'
    return Outcome(label, True, black_points_on_board, black_score, white_points_on_board, white_score)


SPAN = 19
ZOBRIST = [[{color: random.getrandbits(64) for color in Color} for x in range(SPAN)] for y in range(SPAN)]


def build_empty_hash():
    value = 0
    for row in ZOBRIST:
        for cell in row:
            value ^= cell[Color.EMPTY]
    return value


EMPTY_HASH = build_empty_hash()

PASS = (-1, -1)


class Board:
    def __init__(self, source=None):
        if source is None:
            self.cells = [[Color.EMPTY for _ in range(SPAN)] for _ in range(SPAN)]
            self.positionHash = EMPTY_HASH
            self.situationHash = EMPTY_HASH
        else:
            self.cells = [[color for color in row] for row in source.cells]
            self.positionHash = source.positionHash
            self.situationHash = source.situationHash

    def get(self, row, column):
        return self.cells[row][column]

    def set(self, row, column, color):
        zobrist_cell = ZOBRIST[row][column]

        prev_color_situation = self.cells[row][column]
        if color is not prev_color_situation:
            self.situationHash ^= zobrist_cell[prev_color_situation] ^ zobrist_cell[color]

            prev_color_position = position_color(prev_color_situation)
            next_color_position = position_color(color)
            self.positionHash ^= zobrist_cell[prev_color_position] ^ zobrist_cell[next_color_position]

            self.cells[row][column] = color

    def __eq__(self, other):
        return type(other) is Board and self.situationHash == other.situationHash and self.cells == other.cells

    def is_same_position_as(self, other):
        result = False
        if type(other) is Board and self.positionHash == other.positionHash:
            result = True
            for y in range(SPAN):
                if not result:
                    break
                self_row = self.cells[y]
                other_row = other.cells[y]
                for x in range(SPAN):
                    if position_color(self_row[x]) != position_color(other_row[x]):
                        result = False
                        break
        return result

    def __str__(self):
        representation = ''
        for y, row in enumerate(self.cells):
            for x, color in enumerate(row):
                if color is Color.EMPTY:
                    top_edge = y == 0
                    bottom_edge = y == SPAN - 1
                    left_edge = x == 0
                    right_edge = x == SPAN - 1

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
            if y + 1 < SPAN:
                representation += '\n'
        return representation


def get_neighbors(row, column):
    for r, c in [(row - 1, column), (row, column + 1), (row + 1, column), (row, column - 1)]:
        if 0 <= r < SPAN and 0 <= c < SPAN:
            yield (r, c)


class Group:
    def __init__(self, board, start_row, start_column):
        self.bordersBlack = False
        self.bordersWhite = False
        self.liberties = 0
        self.type = position_color(board.get(start_row, start_column))
        self.members = set()

        to_visit = deque([(start_row, start_column)])
        queued = {(start_row, start_column)}
        while to_visit:
            row, column = to_visit.popleft()
            color = board.get(row, column)
            if color is self.type or self.type is Color.EMPTY and color is Color.UNPLAYABLE:
                self.members.add((row, column))
                for coordinate in get_neighbors(row, column):
                    if coordinate not in queued:
                        to_visit.append(coordinate)
                        queued.add(coordinate)
            elif counts_as_liberty(color):
                self.liberties += 1
            elif color is Color.BLACK:
                self.bordersBlack = True
            elif color is Color.WHITE:
                self.bordersWhite = True


class Game:
    def __init__(
            self,
            # initial construction arguments
            compensation=0,
            handicap_placement=None,
            # game extension arguments
            source=None,
            move=None,
            additional_captures=None,
            board=None,
            outcome=None,
            # game ending arguments
            dead_black_stones=None,
            dead_white_stones=None
    ):
        if source is None:
            self.board = Board()
            self.capturesByBlack = 0
            self.capturesByWhite = 0
            self.currentPlayer = (
                Color.BLACK if handicap_placement is None or len(handicap_placement) == 0 else Color.WHITE
            )
            self.compensation = compensation
            self.handicapStones = set(handicap_placement) if handicap_placement else set()
            self.movesPlayed = 0
            self.outcome = IN_PROGRESS
            self.positionCache = {
                self.board.positionHash: (self.board,)
            }
            self.previousMove = None
            self.previousState = None

            if handicap_placement is not None:
                for y, x in handicap_placement:
                    self.board.set(y, x, Color.BLACK)
        elif outcome.is_over() and outcome.get_margin() is not None:
            self.board = board
            self.capturesByBlack = source.capturesByBlack + dead_white_stones
            self.capturesByWhite = source.capturesByWhite + dead_black_stones
            self.compensation = source.compensation
            self.currentPlayer = source.currentPlayer
            self.handicapStones = source.handicapStones
            self.movesPlayed = source.movesPlayed
            self.outcome = outcome
            self.positionCache = source.positionCache
            self.previousMove = source.previousMove
            self.previousState = source
        else:
            self.compensation = source.compensation
            self.handicapStones = source.handicapStones

            self.board = board
            self.capturesByBlack = source.capturesByBlack
            self.capturesByWhite = source.capturesByWhite
            if additional_captures > 0:
                if source.currentPlayer is Color.BLACK:
                    self.capturesByBlack += additional_captures
                else:
                    self.capturesByWhite += additional_captures
            self.currentPlayer = opposite(source.currentPlayer) if not outcome.is_over() else None
            self.movesPlayed = source.movesPlayed + 1
            self.outcome = outcome
            self.previousMove = move
            self.previousState = source

            if move is PASS:
                self.positionCache = source.positionCache
            else:
                self.positionCache = {k: v for k, v in source.positionCache.items()}
                if board.positionHash in self.positionCache:
                    self.positionCache[board.positionHash] = (board, self.positionCache[board.positionHash])

    def is_over(self):
        return self.outcome.is_over()

    def would_pass_end_game(self):
        return self.outcome is IN_PROGRESS and self.previousMove is PASS

    def get_compensation(self):
        return self.compensation

    def get_previous_state(self):
        return self.previousState

    def get_captures_for(self, player):
        value = None
        if player is Color.BLACK:
            value = self.capturesByBlack
        elif player is Color.WHITE:
            value = self.capturesByWhite
        return value

    def get_handicap(self):
        return len(self.handicapStones) if self.handicapStones is not None else 0

    def get_moves_played(self):
        return self.movesPlayed

    def get(self, row, column):
        return self.board.get(row, column)

    def get_previous_move(self):
        return self.previousMove

    def get_current_player(self):
        return self.currentPlayer

    def get_groups_of_stones(self):
        return self._get_groups_for(False)

    def _get_groups_for(self, include_all_groups):
        grouped = set()
        groups = set()
        for row in range(SPAN):
            for column in range(SPAN):
                coordinate = (row, column)
                if coordinate not in grouped:
                    color = self.board.get(row, column)
                    if include_all_groups or color is Color.BLACK or color is Color.WHITE:
                        group = Group(self.board, row, column)
                        groups.add(group)
                        grouped.update(group.members)
        return groups

    def get_all_groups(self):
        return self._get_groups_for(True)

    def get_legal_moves(self):
        moves = set()
        if self.outcome is IN_PROGRESS:
            for row in range(SPAN):
                for column in range(SPAN):
                    if self.board.get(row, column) is Color.EMPTY:
                        moves.add((row, column))
            moves.add(PASS)
        return moves

    def play(self, move):
        self._confirm_moves_are_permitted()
        return self.pass_turn() if move is PASS else self._perform_move(move[0], move[1])

    def _confirm_moves_are_permitted(self):
        if self.outcome is not IN_PROGRESS:
            raise Exception("This Game is over; no further moves may be made (including passes).")

    def pass_turn(self):
        self._confirm_moves_are_permitted()
        return self._pass_but_continue_game() if self.previousMove is not PASS else self._pass_and_end_game()

    def _pass_but_continue_game(self):
        next_board = self._prepare_board_for_next_player(self.board)
        return Game(source=self, move=PASS, additional_captures=0, board=next_board, outcome=IN_PROGRESS)

    def _prepare_board_for_next_player(self, current_board):
        next_board = Board(current_board)
        next_player = opposite(self.currentPlayer)

        for row in range(SPAN):
            for column in range(SPAN):
                color = next_board.get(row, column)
                if counts_as_liberty(color):
                    is_playable = True

                    scratch_pad = Board(current_board)
                    scratch_pad.set(row, column, next_player)
                    captures = Game._remove_captures(scratch_pad, row, column, next_player)
                    if captures == 0:
                        group = Group(scratch_pad, row, column)
                        if group.liberties == 0:
                            is_playable = False

                    if is_playable:
                        if scratch_pad.positionHash in self.positionCache:
                            cons = self.positionCache[scratch_pad.positionHash]
                            while is_playable and cons is not None:
                                is_playable = not scratch_pad.is_same_position_as(cons[0])
                                cons = None if len(cons < 0) else cons[1]

                    next_board.set(row, column, Color.EMPTY if is_playable else Color.UNPLAYABLE)

        return next_board

    @staticmethod
    def _remove_captures(board, start_row, start_column, played_by):
        captures = 0

        other = opposite(played_by)
        for row, column in get_neighbors(start_row, start_column):
            color = board.get(row, column)
            if color is other:
                group = Group(board, row, column)
                if group.liberties == 0:
                    captures += len(group.members)
                    for r, c in group.members:
                        board.set(r, c, Color.EMPTY)

        return captures

    def _pass_and_end_game(self):
        return Game(source=self, move=PASS, additional_captures=0, board=self.board, outcome=COMPLETED_BUT_NOT_SCORED)

    def _perform_move(self, row, column):
        next_board = Board(self.board)
        next_board.set(row, column, self.currentPlayer)
        additional_captures = Game._remove_captures(next_board, row, column, self.currentPlayer)
        next_board = self._prepare_board_for_next_player(next_board)
        return Game(
            source=self,
            move=(row, column),
            additional_captures=additional_captures,
            board=next_board,
            outcome=IN_PROGRESS
        )

    def score(self, dead_groups=None):
        if self.outcome is not COMPLETED_BUT_NOT_SCORED:
            raise Exception('score() may only be called on games that are complete but not scored.')

        dead_black_stones = 0
        dead_white_stones = 0
        clean = Board(self.board)
        if dead_groups:
            for group in dead_groups:
                count = group.members.size()
                if group.type is Color.BLACK:
                    dead_black_stones += count
                elif dead_white_stones is Color.WHITE:
                    dead_white_stones += count
                for row, column in group.members:
                    clean.set(row, column, Color.EMPTY)

        for row in range(SPAN):
            for column in range(SPAN):
                if clean.get(row, column) is Color.UNPLAYABLE:
                    clean.set(row, column, Color.EMPTY)

        black_points_on_board = 0
        black_score = 0
        white_points_on_board = 0
        white_score = self.compensation
        for group in self.get_all_groups():
            points = len(group.members)
            borders_black_only = group.bordersBlack and not group.bordersWhite
            borders_white_only = group.bordersWhite and not group.bordersBlack
            if group.type is Color.BLACK or group.type is Color.EMPTY and borders_black_only:
                black_points_on_board += points
                black_score += points
            elif group.type is Color.WHITE or group.type is Color.EMPTY and borders_white_only:
                white_points_on_board += points
                white_score += points

        final_outcome = finish(black_points_on_board, black_score, white_points_on_board, white_score)
        return Game(
            source=self,
            board=clean,
            dead_black_stones=dead_black_stones,
            dead_white_stones=dead_white_stones,
            outcome=final_outcome
        )

    def resume(self):
        if self.outcome is not COMPLETED_BUT_NOT_SCORED:
            raise Exception('Only a Game that is complete but not score can be resumed.')

        return self.previousState.previousState

    def __str__(self):
        representation = f'{SPAN}x{SPAN} Game {self.outcome}, {self.movesPlayed} Moves'
        if not self.outcome.is_over():
            representation += f', {"Black" if self.currentPlayer is Color.BLACK else "White"} to Play'
        representation += f'\nCompensation {self.compensation}, Handicap {len(self.handicapStones)}'
        if self.handicapStones:
            representation += f' {self.handicapStones}'
        representation += f'\nBlack Captures {self.capturesByBlack}, White Captures {self.capturesByWhite}'
        if self.previousMove:
            if self.previousMove is PASS:
                representation += '\nPrevious Move was Pass'
            else:
                representation += f'\nPrevious Move @ {self.previousMove[1] + 1}-{self.previousMove[0] + 1}'
        representation += f'\n{self.board}'
        return representation
