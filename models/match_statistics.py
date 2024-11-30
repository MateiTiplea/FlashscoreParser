# Location: models/match_statistics.py

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MatchStatistics:
    """Represents detailed statistics for a played match."""

    stats_id: UUID
    match_id: UUID

    #  Expected goals (xG)
    home_expected_goals: Optional[float] = None
    away_expected_goals: Optional[float] = None

    # Ball possession (as integer percentage)
    home_possession: Optional[int] = None
    away_possession: Optional[int] = None

    # Shots
    home_shots_total: Optional[int] = None
    away_shots_total: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    home_shots_off_target: Optional[int] = None
    away_shots_off_target: Optional[int] = None
    home_shots_blocked: Optional[int] = None
    away_shots_blocked: Optional[int] = None

    #  Free kicks
    home_free_kicks: Optional[int] = None
    away_free_kicks: Optional[int] = None

    # Set pieces
    home_corners: Optional[int] = None
    away_corners: Optional[int] = None

    #  Offsides
    home_offsides: Optional[int] = None
    away_offsides: Optional[int] = None

    #  Throw-ins
    home_throw_ins: Optional[int] = None
    away_throw_ins: Optional[int] = None

    #  Goalkeeper saves
    home_goalkeeper_saves: Optional[int] = None
    away_goalkeeper_saves: Optional[int] = None

    # Fouls and cards
    home_fouls: Optional[int] = None
    away_fouls: Optional[int] = None
    home_yellow_cards: Optional[int] = None
    away_yellow_cards: Optional[int] = None
    home_red_cards: Optional[int] = None
    away_red_cards: Optional[int] = None

    #  Passes
    home_total_passes: Optional[int] = None
    away_total_passes: Optional[int] = None
    home_completed_passes: Optional[int] = None
    away_completed_passes: Optional[int] = None

    #  Crosses
    home_crosses: Optional[int] = None
    away_crosses: Optional[int] = None

    #  Interceptions
    home_interceptions: Optional[int] = None
    away_interceptions: Optional[int] = None

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
