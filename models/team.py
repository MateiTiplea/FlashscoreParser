# Location: models/team.py

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Team:
    """Represents a football team."""

    team_id: UUID
    name: str
    team_url: str

    @classmethod
    def create(cls, name: str, team_url: str) -> "Team":
        """Factory method to create a new Team instance with a generated UUID."""
        return cls(team_id=uuid4(), name=name, team_url=team_url)
