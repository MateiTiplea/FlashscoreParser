# Location: models/played_match.py

from dataclasses import dataclass
from typing import Optional

from models.match import Match
from models.match_statistics import MatchStatistics
from models.match_status import MatchStatus
from models.team import Team


@dataclass
class PlayedMatch(Match):
    """
    Represents a completed football match with final score and statistics.
    Extends the base Match class with additional fields specific to completed matches.
    """

    home_score: int
    away_score: int
    statistics: Optional[MatchStatistics] = None

    @classmethod
    def create(
        cls,
        match_url: str,
        country: str,
        competition: str,
        match_date: str,
        round: Optional[str],
        home_team: Team,
        away_team: Team,
        home_score: int,
        away_score: int,
        statistics: Optional[MatchStatistics] = None,
        status: MatchStatus = MatchStatus.FINISHED,
    ) -> "PlayedMatch":
        """
        Factory method to create a new PlayedMatch instance.

        Args:
            match_url: The URL of the match on Flashscore
            country: The country where the match took place
            competition: The name of the competition/league
            match_date: The date and time when the match was played
            round: The round/matchday of the competition (optional)
            home_team: The home team
            away_team: The away team
            home_score: Number of goals scored by home team
            away_score: Number of goals scored by away team
            statistics: Detailed match statistics (optional)
            status: The status of the match (defaults to FINISHED)

        Returns:
            A new PlayedMatch instance
        """
        # Create base match first
        match = super().create(
            match_url=match_url,
            country=country,
            competition=competition,
            match_date=match_date,
            round=round,
            home_team=home_team,
            away_team=away_team,
            status=status,
        )

        # Add played match specific fields
        return cls(
            match_id=match.match_id,
            match_url=match.match_url,
            country=match.country,
            competition=match.competition,
            match_date=match.match_date,
            round=match.round,
            home_team=match.home_team,
            away_team=match.away_team,
            status=match.status,
            home_score=home_score,
            away_score=away_score,
            statistics=statistics,
        )

    def __str__(self) -> str:
        """Return a string representation including the score."""
        return (
            f"{self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name} "
            f"({self.competition}, {self.country})"
        )

    def get_winner(self) -> Optional[Team]:
        """Returns the winning team, or None if it was a draw."""
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None

    def is_draw(self) -> bool:
        """Returns True if the match ended in a draw."""
        return self.home_score == self.away_score

    def get_goal_difference(self) -> int:
        """Returns the goal difference (positive for home win, negative for away win)."""
        return self.home_score - self.away_score

    def get_total_goals(self) -> int:
        """Returns the total number of goals scored in the match."""
        return self.home_score + self.away_score
