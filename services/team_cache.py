#  Location: services/team_cache.py

from typing import Dict, Optional
from uuid import UUID

from models.team import Team


class TeamCache:
    """
    Cache for Team objects to avoid redundant data extraction.
    Teams can be cached and retrieved by URL or name.
    """

    def __init__(self):
        """Initialize empty cache dictionaries."""
        self._cache_by_url: Dict[str, Team] = {}
        self._cache_by_name: Dict[str, Team] = {}
        self._cache_by_id: Dict[UUID, Team] = {}

    def add_team(self, team: Team) -> None:
        """
        Add a team to all cache dictionaries.

        Args:
            team: Team object to cache
        """
        self._cache_by_url[team.team_url] = team
        self._cache_by_name[team.name] = team
        self._cache_by_id[team.team_id] = team

    def get_by_url(self, url: str) -> Optional[Team]:
        """
        Retrieve a team by its URL.

        Args:
            url: Team's URL

        Returns:
            Team object if found in cache, None otherwise
        """
        return self._cache_by_url.get(url)

    def get_by_name(self, name: str) -> Optional[Team]:
        """
        Retrieve a team by its name.

        Args:
            name: Team's name

        Returns:
            Team object if found in cache, None otherwise
        """
        return self._cache_by_name.get(name)

    def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """
        Retrieve a team by its ID.

        Args:
            team_id: Team's UUID

        Returns:
            Team object if found in cache, None otherwise
        """
        return self._cache_by_id.get(team_id)

    def contains_url(self, url: str) -> bool:
        """
        Check if a team URL exists in the cache.

        Args:
            url: Team's URL

        Returns:
            True if team exists in cache, False otherwise
        """
        return url in self._cache_by_url

    def contains_name(self, name: str) -> bool:
        """
        Check if a team name exists in the cache.

        Args:
            name: Team's name

        Returns:
            True if team exists in cache, False otherwise
        """
        return name in self._cache_by_name

    def contains_id(self, team_id: UUID) -> bool:
        """
        Check if a team ID exists in the cache.

        Args:
            team_id: Team's UUID

        Returns:
            True if team exists in cache, False otherwise
        """
        return team_id in self._cache_by_id

    def clear(self) -> None:
        """Clear all cache dictionaries."""
        self._cache_by_url.clear()
        self._cache_by_name.clear()
        self._cache_by_id.clear()

    @property
    def size(self) -> int:
        """
        Get the number of teams in the cache.

        Returns:
            Number of cached teams
        """
        return len(self._cache_by_url)
