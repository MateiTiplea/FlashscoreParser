# Location: models/match_statistics.py

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MatchStatistics:
    """Represents detailed statistics for a played match."""

    stats_id: UUID
    match_id: UUID

    # Ball possession (as percentage)
    home_possession: Optional[float] = None
    away_possession: Optional[float] = None

    # Shots
    home_shots_total: Optional[int] = None
    away_shots_total: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    home_shots_off_target: Optional[int] = None
    away_shots_off_target: Optional[int] = None

    # Set pieces
    home_corners: Optional[int] = None
    away_corners: Optional[int] = None

    # Fouls and cards
    home_fouls: Optional[int] = None
    away_fouls: Optional[int] = None
    home_yellow_cards: Optional[int] = None
    away_yellow_cards: Optional[int] = None
    home_red_cards: Optional[int] = None
    away_red_cards: Optional[int] = None

    # Offsides
    home_offsides: Optional[int] = None
    away_offsides: Optional[int] = None

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
