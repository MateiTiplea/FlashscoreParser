# Location: models/played_match.py

from dataclasses import dataclass
from datetime import datetime
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
        match_date: datetime,
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
        # Create base match first using parent class's create method
        base_match = Match.create(
            match_url=match_url,
            country=country,
            competition=competition,
            match_date=match_date,
            round=round,
            home_team=home_team,
            away_team=away_team,
            status=status,
        )

        # Create PlayedMatch instance with all fields
        return cls(
            match_id=base_match.match_id,
            match_url=base_match.match_url,
            country=base_match.country,
            competition=base_match.competition,
            match_date=base_match.match_date,
            round=base_match.round,
            home_team=base_match.home_team,
            away_team=base_match.away_team,
            status=base_match.status,
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

    # def __repr__(self) -> str:
    #     """Return a string representation of the played match."""
    #     return (
    #         f"PlayedMatch(match_id={self.match_id}, match_url={self.match_url}, "
    #         f"country={self.country}, competition={self.competition}, "
    #         f"match_date={self.match_date}, round={self.round}, "
    #         f"home_team={self.home_team}, away_team={self.away_team}, "
    #         f"status={self.status}, home_score={self.home_score}, "
    #         f"away_score={self.away_score}, statistics={self.statistics})"
    #     )

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
