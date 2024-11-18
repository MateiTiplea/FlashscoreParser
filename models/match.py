import json

from models.team import Team


class Match:
    def __init__(
        self,
        match_url: str,
        competition: str,
        home_team_name: str,
        away_team_name: str,
        match_date: str,
        round: str,
    ):
        self.match_url = match_url
        self.home_team = Team(home_team_name)
        self.away_team = Team(away_team_name)
        self.match_date = match_date
        self.competition = competition
        self.round = round

    def to_dict(self):
        return {
            "match_url": self.match_url,
            "competition": self.competition,
            "home_team": self.home_team.to_dict(),
            "away_team": self.away_team.to_dict(),
            "match_date": self.match_date,
            "round": self.round,
        }

    def __str__(self):
        return (
            f"Match(competition={self.competition}, home_team={self.home_team}, "
            f"away_team={self.away_team}, match_date={self.match_date}, round={self.round})"
        )
