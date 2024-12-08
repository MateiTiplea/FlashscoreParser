# Location: models/fixture_match.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.head_to_head import HeadToHead
from models.match import Match
from models.team import Team
from models.team_form import TeamForm


@dataclass(init=True)
class FixtureMatch(Match):
    """
    Represents an upcoming football match with form and head-to-head data.
    Extends the base Match class with additional predictive information.
    """

    home_team_form: Optional[TeamForm] = None
    away_team_form: Optional[TeamForm] = None
    head_to_head: Optional[HeadToHead] = None

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
        home_team_form: Optional[TeamForm] = None,
        away_team_form: Optional[TeamForm] = None,
        head_to_head: Optional[HeadToHead] = None,
    ) -> "FixtureMatch":
        """
        Factory method to create a new FixtureMatch instance.

        Args:
            match_url: The URL of the match on Flashscore
            country: The country where the match will take place
            competition: The name of the competition/league
            match_date: The scheduled date and time of the match
            round: The round/matchday of the competition (optional)
            home_team: The home team
            away_team: The away team
            home_team_form: Recent form of the home team (optional)
            away_team_form: Recent form of the away team (optional)
            head_to_head: Head-to-head record between the teams (optional)

        Returns:
            A new FixtureMatch instance
        """
        # Create base match first
        base_match = super().create(
            match_url=match_url,
            country=country,
            competition=competition,
            match_date=match_date,
            round=round,
            home_team=home_team,
            away_team=away_team,
        )

        # Return new FixtureMatch with all fields
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
            home_team_form=home_team_form,
            away_team_form=away_team_form,
            head_to_head=head_to_head,
        )

    def get_days_until_match(self) -> int:
        """Returns the number of days until the match."""
        today = datetime.now()
        return (self.match_date.date() - today.date()).days
