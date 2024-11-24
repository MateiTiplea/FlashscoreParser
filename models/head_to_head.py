# Location: models/head_to_head.py

from dataclasses import dataclass
from typing import List
from uuid import UUID, uuid4

from models.played_match import PlayedMatch
from models.team import Team


@dataclass
class HeadToHead:
    """
    Represents the head-to-head record between two teams.
    Includes their most recent matches against each other.
    """

    h2h_id: UUID
    team_a: Team
    team_b: Team
    matches: List[PlayedMatch]

    @classmethod
    def create(
        cls, team_a: Team, team_b: Team, matches: List[PlayedMatch]
    ) -> "HeadToHead":
        """
        Factory method to create a new HeadToHead instance.

        Args:
            team_a: First team
            team_b: Second team
            matches: List of recent matches between these teams

        Returns:
            A new HeadToHead instance
        """
        return cls(h2h_id=uuid4(), team_a=team_a, team_b=team_b, matches=matches)

    def get_team_record(self, team: Team) -> tuple[int, int, int]:
        """
        Get wins, draws, losses for specified team against the other team.

        Args:
            team: The team to get the record for

        Returns:
            Tuple of (wins, draws, losses)
        """
        if team not in (self.team_a, self.team_b):
            raise ValueError("Specified team is not part of this head-to-head record")

        wins = draws = losses = 0
        for match in self.matches:
            winner = match.get_winner()
            if winner == team:
                wins += 1
            elif winner is None:
                draws += 1
            else:
                losses += 1

        return (wins, draws, losses)
