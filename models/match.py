# Location: models/match.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from models.match_status import MatchStatus
from models.team import Team


@dataclass
class Match:
    """
    Base class representing a football match.
    Contains common attributes for both fixtures and played matches.
    """

    match_id: UUID
    match_url: str
    country: str
    competition: str
    match_date: datetime
    round: Optional[str]
    home_team: Team
    away_team: Team
    status: MatchStatus

    @classmethod
    def create(
        cls,
        match_url: str,
        country: str,
        competition: str,
        match_date: datetime,
        round: Optional[str],
        home_team: Team,
        away_team: Team,
        status: MatchStatus = MatchStatus.SCHEDULED,
    ) -> "Match":
        """
        Factory method to create a new Match instance with a generated UUID.

        Args:
            match_url: The URL of the match on Flashscore
            country: The country where the match is taking place
            competition: The name of the competition/league
            match_date: The scheduled date and time of the match
            round: The round/matchday of the competition (optional)
            home_team: The home team
            away_team: The away team
            status: The current status of the match (defaults to SCHEDULED)

        Returns:
            A new Match instance
        """
        return cls(
            match_id=uuid4(),
            match_url=match_url,
            country=country,
            competition=competition,
            match_date=match_date,
            round=round,
            home_team=home_team,
            away_team=away_team,
            status=status,
        )

    def __str__(self) -> str:
        """Return a string representation of the match."""
        return (
            f"{self.home_team.name} vs {self.away_team.name} - "
            f"{self.competition} ({self.country}) - "
            f"{self.match_date.strftime('%Y-%m-%d %H:%M')}"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the match."""
        return (
            f"Match(id={self.match_id}, "
            f"teams='{self.home_team.name} vs {self.away_team.name}', "
            f"competition='{self.competition}', "
            f"date='{self.match_date.strftime('%Y-%m-%d %H:%M')}')"
        )
