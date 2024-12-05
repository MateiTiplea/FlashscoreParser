import json
from pathlib import Path
from typing import Any, Dict, List

from logging_config import get_logger
from models.fixture_match import FixtureMatch
from models.head_to_head import HeadToHead
from models.played_match import PlayedMatch
from models.team import Team
from models.team_form import TeamForm


class JsonSerializationService:
    """
    Handles serialization of all models to JSON format.
    Manages relationships between objects and handles custom type serialization.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize service with output directory.

        Args:
            output_dir: Directory to save JSON files
        """
        self.output_dir = output_dir
        self.logger = get_logger(__name__)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def serialize_fixtures_data(
        self, fixtures: List[FixtureMatch], errors: Dict[str, List[str]]
    ) -> None:
        """
        Serialize fixtures data and errors to JSON files.

        Args:
            fixtures: List of FixtureMatch objects
            errors: Dictionary of errors by category
        """
        try:
            # Serialize fixtures
            fixtures_data = self._serialize_fixtures(fixtures)
            self._write_json(fixtures_data, "fixtures.json")

            # Write errors if any
            if any(errors.values()):
                self._write_json(errors, "errors.json")

            self.logger.info(
                f"Successfully serialized {len(fixtures)} fixtures to {self.output_dir}"
            )

        except Exception as e:
            self.logger.error(f"Error serializing data: {str(e)}")
            raise

    def _serialize_fixtures(self, fixtures: List[FixtureMatch]) -> List[Dict[str, Any]]:
        """
        Serialize list of FixtureMatch objects.

        Args:
            fixtures: List of FixtureMatch objects

        Returns:
            List of serialized fixtures as dictionaries
        """
        return [self._serialize_fixture(fixture) for fixture in fixtures]

    def _serialize_fixture(self, fixture: FixtureMatch) -> Dict[str, Any]:
        """
        Serialize a single FixtureMatch object.

        Args:
            fixture: FixtureMatch object to serialize

        Returns:
            Dictionary representation of the fixture
        """
        return {
            "match_id": str(fixture.match_id),
            "match_url": fixture.match_url,
            "country": fixture.country,
            "competition": fixture.competition,
            "match_date": fixture.match_date.isoformat(),
            "round": fixture.round,
            "home_team": self._serialize_team(fixture.home_team),
            "away_team": self._serialize_team(fixture.away_team),
            "status": fixture.status.name,
            "home_team_form": (
                self._serialize_team_form(fixture.home_team_form)
                if fixture.home_team_form
                else None
            ),
            "away_team_form": (
                self._serialize_team_form(fixture.away_team_form)
                if fixture.away_team_form
                else None
            ),
            "head_to_head": (
                self._serialize_head_to_head(fixture.head_to_head)
                if fixture.head_to_head
                else None
            ),
        }

    def _serialize_team(self, team: Team) -> Dict[str, Any]:
        """Serialize Team object."""
        return {
            "team_id": str(team.team_id),
            "name": team.name,
            "team_url": team.team_url,
            "country": team.country,
            "stadium": team.stadium,
            "stadium_city": team.stadium_city,
            "capacity": team.capacity,
        }

    def _serialize_team_form(self, form: TeamForm) -> Dict[str, Any]:
        """Serialize TeamForm object."""
        return {
            "form_id": str(form.form_id),
            "team": self._serialize_team(form.team),
            "matches": [self._serialize_played_match(match) for match in form.matches],
            "period_start": form.period_start.isoformat(),
            "period_end": form.period_end.isoformat(),
            "summary": {
                "wins": form.get_wins(),
                "draws": form.get_draws(),
                "losses": form.get_losses(),
                "goals_scored": form.get_goals_scored(),
                "goals_conceded": form.get_goals_conceded(),
            },
        }

    def _serialize_head_to_head(self, h2h: HeadToHead) -> Dict[str, Any]:
        """Serialize HeadToHead object."""
        return {
            "h2h_id": str(h2h.h2h_id),
            "team_a": self._serialize_team(h2h.team_a),
            "team_b": self._serialize_team(h2h.team_b),
            "matches": [self._serialize_played_match(match) for match in h2h.matches],
            "summary": {
                "team_a_record": h2h.get_team_record(h2h.team_a),
                "team_b_record": h2h.get_team_record(h2h.team_b),
            },
        }

    def _serialize_played_match(self, match: PlayedMatch) -> Dict[str, Any]:
        """Serialize PlayedMatch object."""
        return {
            "match_id": str(match.match_id),
            "match_url": match.match_url,
            "country": match.country,
            "competition": match.competition,
            "match_date": match.match_date.isoformat(),
            "round": match.round,
            "home_team": self._serialize_team(match.home_team),
            "away_team": self._serialize_team(match.away_team),
            "status": match.status.name,
            "home_score": match.home_score,
            "away_score": match.away_score,
        }

    def _write_json(self, data: Any, filename: str) -> None:
        """
        Write data to JSON file.

        Args:
            data: Data to serialize
            filename: Name of the output file
        """
        output_path = self.output_dir / filename
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error writing {filename}: {str(e)}")
            raise
