# Location: models/team_form.py

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from models.played_match import PlayedMatch
from models.team import Team


@dataclass
class TeamForm:
    """
    Represents a team's recent form over a specific period.
    Includes the last k matches played by the team.
    """

    form_id: UUID
    team: Team
    matches: List[PlayedMatch]
    period_start: datetime
    period_end: datetime

    @classmethod
    def create(cls, team: Team, matches: List[PlayedMatch]) -> "TeamForm":
        """
        Factory method to create a new TeamForm instance.

        Args:
            team: The team whose form is being tracked
            matches: List of recent matches, should be in chronological order

        Returns:
            A new TeamForm instance with calculated period dates
        """
        if not matches:
            raise ValueError("At least one match is required to create team form")

        # Get period start and end from match dates
        period_start = min(match.match_date for match in matches)
        period_end = max(match.match_date for match in matches)

        return cls(
            form_id=uuid4(),
            team=team,
            matches=matches,
            period_start=period_start,
            period_end=period_end,
        )

    def get_wins(self) -> int:
        """Returns the number of wins in the form period."""
        return sum(1 for match in self.matches if match.get_winner() == self.team)

    def get_draws(self) -> int:
        """Returns the number of draws in the form period."""
        return sum(1 for match in self.matches if match.is_draw())

    def get_losses(self) -> int:
        """Returns the number of losses in the form period."""
        return len(self.matches) - self.get_wins() - self.get_draws()

    def get_goals_scored(self) -> int:
        """Returns total goals scored by the team in the form period."""
        return sum(
            match.home_score if match.home_team == self.team else match.away_score
            for match in self.matches
        )

    def get_goals_conceded(self) -> int:
        """Returns total goals conceded by the team in the form period."""
        return sum(
            match.away_score if match.home_team == self.team else match.home_score
            for match in self.matches
        )
