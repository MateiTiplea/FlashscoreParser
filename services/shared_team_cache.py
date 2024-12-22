from multiprocessing import Manager
from typing import Dict, Optional
from uuid import UUID

from models.team import Team

from .team_cache_protocol import TeamCacheProtocol


class SharedTeamCache(TeamCacheProtocol):
    """Process-safe shared cache for Team objects"""

    def __init__(self):
        manager = Manager()
        self._cache_by_url = manager.dict()
        self._cache_by_name = manager.dict()
        self._cache_by_id = manager.dict()

    def add_team(self, team: Team) -> None:
        self._cache_by_url[team.team_url] = team
        self._cache_by_name[team.name] = team
        self._cache_by_id[str(team.team_id)] = team

    def get_by_url(self, url: str) -> Optional[Team]:
        return self._cache_by_url.get(url)

    def get_by_name(self, name: str) -> Optional[Team]:
        return self._cache_by_name.get(name)

    def get_by_id(self, team_id: UUID) -> Optional[Team]:
        return self._cache_by_id.get(str(team_id))

    def contains_url(self, url: str) -> bool:
        return url in self._cache_by_url

    def contains_name(self, name: str) -> bool:
        return name in self._cache_by_name

    def contains_id(self, team_id: UUID) -> bool:
        return str(team_id) in self._cache_by_id

    def clear(self) -> None:
        self._cache_by_url.clear()
        self._cache_by_name.clear()
        self._cache_by_id.clear()

    @property
    def size(self) -> int:
        return len(self._cache_by_url)
