from typing import Dict, Optional, Protocol
from uuid import UUID

from models.team import Team


class TeamCacheProtocol(Protocol):
    """Protocol defining the interface for team caching implementations."""

    def add_team(self, team: Team) -> None:
        """
        Add a team to all cache dictionaries.

        Args:
            team: Team object to cache
        """
        ...

    def get_by_url(self, url: str) -> Optional[Team]:
        """
        Retrieve a team by its URL.

        Args:
            url: Team's URL

        Returns:
            Team object if found in cache, None otherwise
        """
        ...

    def get_by_name(self, name: str) -> Optional[Team]:
        """
        Retrieve a team by its name.

        Args:
            name: Team's name

        Returns:
            Team object if found in cache, None otherwise
        """
        ...

    def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """
        Retrieve a team by its ID.

        Args:
            team_id: Team's UUID

        Returns:
            Team object if found in cache, None otherwise
        """
        ...

    def contains_url(self, url: str) -> bool:
        """
        Check if a team URL exists in the cache.

        Args:
            url: Team's URL

        Returns:
            True if team exists in cache, False otherwise
        """
        ...

    def contains_name(self, name: str) -> bool:
        """
        Check if a team name exists in the cache.

        Args:
            name: Team's name

        Returns:
            True if team exists in cache, False otherwise
        """
        ...

    def contains_id(self, team_id: UUID) -> bool:
        """
        Check if a team ID exists in the cache.

        Args:
            team_id: Team's UUID

        Returns:
            True if team exists in cache, False otherwise
        """
        ...

    def clear(self) -> None:
        """Clear all cache dictionaries."""
        ...

    @property
    def size(self) -> int:
        """
        Get the number of teams in the cache.

        Returns:
            Number of cached teams
        """
        ...
