# Location: services/factories/fixture_match_factory.py

from typing import Optional

from browsers.base_browser import BaseBrowser
from logging_config import get_logger
from models.fixture_match import FixtureMatch
from models.head_to_head import HeadToHead
from models.team_form import TeamForm
from services.factories.match_factory import MatchFactory
from services.factories.team_factory import TeamFactory
from services.head_to_head_service import HeadToHeadService
from services.team_form_service import TeamFormService


class FixtureMatchFactory(MatchFactory):
    """
    Factory class for creating FixtureMatch objects.
    Extends MatchFactory to add form and head-to-head data extraction.
    """

    def __init__(
        self,
        browser: BaseBrowser,
        team_factory: TeamFactory,
        team_form_service: TeamFormService,
        h2h_service: HeadToHeadService,
    ):
        """
        Initialize with required services.

        Args:
            browser: Browser instance for web interactions
            team_factory: Factory for creating Team objects
            team_form_service: Service for getting team form data
            h2h_service: Service for getting head-to-head data
        """
        super().__init__(browser, team_factory)
        self.team_form_service = team_form_service
        self.h2h_service = h2h_service
        self.logger = get_logger(__name__)

    def create_fixture_match(self, match_url: str) -> Optional[FixtureMatch]:
        """
        Create a FixtureMatch object by extracting all match data.

        Args:
            match_url: URL of the match page

        Returns:
            FixtureMatch object if extraction successful, None otherwise
        """
        try:
            # Get base match data using parent class
            base_match = super().create_match(match_url)
            if not base_match:
                return None

            # Extract form data for both teams
            home_form = self._get_team_form(base_match.home_team)
            away_form = self._get_team_form(base_match.away_team)

            # Extract head-to-head data
            h2h = self._get_head_to_head(
                match_url, base_match.home_team, base_match.away_team
            )

            # Create fixture match
            return FixtureMatch.create(
                match_url=base_match.match_url,
                country=base_match.country,
                competition=base_match.competition,
                match_date=base_match.match_date,
                round=base_match.round,
                home_team=base_match.home_team,
                away_team=base_match.away_team,
                home_team_form=home_form,
                away_team_form=away_form,
                head_to_head=h2h,
            )

        except Exception as e:
            self.logger.error(f"Error creating fixture match object: {str(e)}")
            return None

    def _get_team_form(self, team) -> Optional[TeamForm]:
        """
        Get form data for a team using TeamFormService.

        Args:
            team: Team object to get form for

        Returns:
            TeamForm object if available, None otherwise
        """
        try:
            return self.team_form_service.get_team_form(team)
        except Exception as e:
            self.logger.error(f"Error getting form for team {team.name}: {str(e)}")
            return None

    def _get_head_to_head(
        self, match_url, home_team, away_team
    ) -> Optional[HeadToHead]:
        """
        Get head-to-head data using HeadToHeadService.

        Args:
            home_team: Home team object
            away_team: Away team object

        Returns:
            HeadToHead object if available, None otherwise
        """
        try:
            return self.h2h_service.get_head_to_head(match_url, home_team, away_team)
        except Exception as e:
            self.logger.error(
                f"Error getting H2H for {home_team.name} vs {away_team.name}: {str(e)}"
            )
            return None
