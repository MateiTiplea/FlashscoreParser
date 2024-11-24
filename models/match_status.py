# Location: models/match_status.py

from enum import Enum, auto


class MatchStatus(Enum):
    """Enum representing the possible states of a match."""

    SCHEDULED = auto()  # Match is scheduled but hasn't started
    LIVE = auto()  # Match is currently being played
    FINISHED = auto()  # Match has been completed
    POSTPONED = auto()  # Match has been postponed
    CANCELLED = auto()  # Match has been cancelled
    ABANDONED = auto()  # Match was started but abandoned before completion
