# Location: services/data_extraction_coordinator.py

from typing import Optional

from browsers.base_browser import BaseBrowser
from logging_config import get_logger
from models.config import Config
from models.fixture_match import FixtureMatch
from services.factories.fixture_match_factory import FixtureMatchFactory
from services.factories.played_match_factory import PlayedMatchFactory
from services.factories.team_factory import TeamFactory
from services.head_to_head_service import HeadToHeadService
from services.shared_team_cache import SharedTeamCache
from services.team_form_service import TeamFormService


class DataExtractionCoordinator:
    """
    Coordinates the data extraction process for a single browser instance.
    Each process should have its own coordinator instance.
    """

    def __init__(self, browser: BaseBrowser, config: Config):
        """
        Initialize coordinator with browser and config.

        Args:
            browser: Browser instance for web interactions
            config: Configuration containing country, league, and rounds info
        """
        self.browser = browser
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize shared cache
        self.team_cache = SharedTeamCache()

        # Initialize services
        self._initialize_services()

    def _initialize_services(self) -> None:
        """Initialize all required services for this coordinator instance."""
        # Initialize team factory
        self.team_factory = TeamFactory(browser=self.browser, cache=self.team_cache)

        # Initialize match factory
        self.played_match_factory = PlayedMatchFactory(
            browser=self.browser, team_factory=self.team_factory
        )

        # Initialize supporting services
        self.team_form_service = TeamFormService(
            browser=self.browser,
            played_match_factory=self.played_match_factory,
            form_matches=5,
        )

        self.h2h_service = HeadToHeadService(
            browser=self.browser,
            played_match_factory=self.played_match_factory,
            max_matches=5,
        )

        # Initialize fixture match factory
        self.fixture_match_factory = FixtureMatchFactory(
            browser=self.browser,
            team_factory=self.team_factory,
            team_form_service=self.team_form_service,
            h2h_service=self.h2h_service,
        )

    def create_fixture_match(self, fixture_url: str) -> Optional[FixtureMatch]:
        """
        Create a fixture match from a URL.

        Args:
            fixture_url: URL of the fixture to process

        Returns:
            FixtureMatch object if successful, None otherwise
        """
        try:
            self.logger.debug(f"Processing fixture: {fixture_url}")
            return self.fixture_match_factory.create_fixture_match(fixture_url)
        except Exception as e:
            self.logger.error(
                f"Error creating fixture match from {fixture_url}: {str(e)}"
            )
            return None

    def cleanup(self) -> None:
        """Clean up resources used by this coordinator instance."""
        try:
            self.team_cache.clear()
            self.logger.info("Successfully cleaned up resources")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
