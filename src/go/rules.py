#!/usr/bin/env python3

from enum import auto, Enum


class Counting(Enum):
    """
    AREA: Points surrounded + living stones.
    CHINESE: Target = (Points on board - unscored points) / 2.  Black - compensation / 2 must be >= this number.
    TERRITORY: Points surrounded + stones captured.  Groups in seki might not score; see Tax.
    """
    AREA = auto()
    CHINESE = auto()
    TERRITORY = auto()


class DeadStones(Enum):
    """
    REMOVED_BY_AGREEMENT: The players must agree on which stones are dead before scoring the game.
    ALIVE_IF_ON_BOARD: Any group left on the board after passing must be alive.
    """
    REMOVED_BY_AGREEMENT = auto()
    ALIVE_IF_ON_BOARD = auto()


class HandicapPlacement(Enum):
    """
    FIXED: There are standardized handicap placements.
    FREE: Black may place his handicap stones as though White is passing between his moves.
    """
    FIXED = auto()
    FREE = auto()


class GameEnd(Enum):
    """
    TWO_PASSES: If each player passes, the game ends.
    SECOND_PASSES_LAST: Whoever played second must pass last.  In even and one-stone handicap games, this is White.  In
      higher handicap games, this is Black.  This can lead to three passes to end the game.
    """
    TWO_PASSES = auto()
    SECOND_PASSES_LAST = auto()


class Ko(Enum):
    """
    SIMPLE: A player cannot recreate the previous position with a board play.  This can lead to games being invalidated.
    POSITIONAL: No board position can be repeated by a board play.
    SITUATIONAL: Technically natural situational.  A player cannot recreate a board position he created with a board
      play, even if he is using a different move.  Situational Superko forbids recreating a position created with a
      pass, too.
    SEND_TWO_RETURN_ONE: This is a modification of the SIMPLE rule that also forbids a player from sending two stones
      then returning one.
    """
    SIMPLE = auto()
    POSITIONAL = auto()
    SITUATIONAL = auto()
    SEND_TWO_RETURN_ONE = auto()


class PassStone(Enum):
    """
    NO: Passing is free.
    YES: Passing costs a stone.
    """
    NO = auto()
    YES = auto()


class SekiScoring(Enum):
    """
    NO: Eyes in a seki do not give points.
    YES: Eyes in a seki do give points.
    """
    NO = auto()
    YES = auto()


class Suicide(Enum):
    """
    NO: A player is forbidden to play a self-capture as his move.
    YES: A player is permitted to play a self-capture as his move.
    """
    NO = auto()
    YES = auto()


class WhiteHandicapBonus(Enum):
    """
    NONE: White gets no compensation for Black's handicap stones.
    N: White gets a point for each handicap stone Black placed.
    N_MINUS_ONE: White gets one less point than the number of handicap stones Black placed.
    """
    NONE = auto()
    N = auto()
    N_MINUS_ONE = auto()


class RuleSet:
    def __init__(
        self,
        counting: Counting,
        dead_stones: DeadStones,
        handicap_placement: HandicapPlacement,
        game_end: GameEnd,
        ko: Ko,
        pass_stone: PassStone,
        seki_scoring: SekiScoring,
        suicide: Suicide,
        white_handicap_bonus: WhiteHandicapBonus
    ):
        self.counting = counting
        self.dead_stones = dead_stones
        self.handicap_placement = handicap_placement
        self.game_end = game_end
        self.ko = ko
        self.pass_stone = pass_stone
        self.seki_scoring = seki_scoring
        self.suicide = suicide
        self.white_handicap_bonus = white_handicap_bonus


AGA = RuleSet(
    Counting.AREA,
    DeadStones.REMOVED_BY_AGREEMENT,
    HandicapPlacement.FIXED,
    GameEnd.SECOND_PASSES_LAST,
    Ko.SITUATIONAL,
    PassStone.YES,
    SekiScoring.YES,
    Suicide.NO,
    WhiteHandicapBonus.N_MINUS_ONE
)

CHINESE = RuleSet(
    Counting.CHINESE,
    DeadStones.REMOVED_BY_AGREEMENT,
    HandicapPlacement.FREE,
    GameEnd.TWO_PASSES,
    Ko.SEND_TWO_RETURN_ONE,
    PassStone.NO,
    SekiScoring.YES,
    Suicide.FORBIDDEN,
    WhiteHandicapBonus.N
)

JAPANESE = RuleSet(
    Counting.TERRITORY,
    DeadStones.REMOVED_BY_AGREEMENT,
    HandicapPlacement.FIXED,
    GameEnd.TWO_PASSES,
    Ko.SIMPLE,
    PassStone.NO,
    SekiScoring.NO,
    Suicide.FORBIDDEN,
    WhiteHandicapBonus.NONE
)

TRAINING = RuleSet(
    Counting.AREA,
    DeadStones.REMOVED_BY_AGREEMENT,
    HandicapPlacement.FIXED,
    GameEnd.TWO_PASSES,
    Ko.POSITIONAL,
    PassStone.NO,
    SekiScoring.YES,
    Suicide.NO,
    WhiteHandicapBonus.N_MINUS_ONE
)

TROMP_TAYLOR = RuleSet(
    Counting.AREA,
    DeadStones.ALIVE_IF_ON_BOARD,
    HandicapPlacement.FREE,
    GameEnd.TWO_PASSES,
    Ko.POSITIONAL,
    PassStone.NO,
    SekiScoring.YES,
    Suicide.YES,
    WhiteHandicapBonus.N_MINUS_ONE
)
