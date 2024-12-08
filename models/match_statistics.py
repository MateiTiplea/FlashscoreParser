# Location: models/match_statistics.py

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, TypedDict
from uuid import UUID, uuid4


class Statistic(TypedDict):
    home: str | int | float
    away: str | int | float


@dataclass
class MatchStatistics:
    """Represents detailed statistics for a played match."""

    stats_id: UUID
    match_id: UUID

    #  Expected goals (xG)
    expected_goals: Optional[Statistic] = None

    # Ball possession (as integer percentage)
    ball_possession: Optional[Statistic] = None

    # Shots
    goal_attempts: Optional[Statistic] = None
    shots_on_goal: Optional[Statistic] = None
    shots_off_goal: Optional[Statistic] = None
    blocked_shots: Optional[Statistic] = None

    #  Big chances
    big_chances: Optional[Statistic] = None

    corner_kicks: Optional[Statistic] = None
    shots_inside_box: Optional[Statistic] = None
    shots_outside_box: Optional[Statistic] = None
    hit_woodwork: Optional[Statistic] = None

    headed_goals: Optional[Statistic] = None

    goalkeeper_saves: Optional[Statistic] = None

    #  Free kicks
    free_kicks: Optional[Statistic] = None

    #  Offsides
    offsides: Optional[Statistic] = None

    # Fouls and cards
    fouls: Optional[Statistic] = None
    yellow_cards: Optional[Statistic] = None
    red_cards: Optional[Statistic] = None
    #  Throw-ins
    throw_ins: Optional[Statistic] = None

    touches_in_opposition_box: Optional[Statistic] = None

    #  Passes
    total_passes: Optional[Statistic] = None
    completed_passes: Optional[Statistic] = None
    total_passes_in_final_third: Optional[Statistic] = None
    completed_passes_in_final_third: Optional[Statistic] = None

    #  Crosses
    total_crosses: Optional[Statistic] = None
    completed_crosses: Optional[Statistic] = None

    #  Tackles
    total_tackles: Optional[Statistic] = None
    won_tackles: Optional[Statistic] = None

    #  Clearances
    clearances: Optional[Statistic] = None

    #  Interceptions
    interceptions: Optional[Statistic] = None

    @classmethod
    def create(cls, match_id: UUID, **statistics) -> "MatchStatistics":
        """
        Factory method to create match statistics with a generated UUID.

        Args:
            match_id: UUID of the associated match
            **statistics: Keyword arguments for various statistics fields

        Returns:
            A new MatchStatistics instance
        """
        return cls(stats_id=uuid4(), match_id=match_id, **statistics)
