from typing import Dict, List, Tuple

from tqdm import tqdm

from browsers.base_browser import BaseBrowser
from logging_config import get_logger
from models.config import Config
from models.fixture_match import FixtureMatch
from services.factories.fixture_match_factory import FixtureMatchFactory
from services.factories.fixtures_url_factory import FixturesURLFactory
from services.factories.played_match_factory import PlayedMatchFactory
from services.factories.team_factory import TeamFactory
from services.head_to_head_service import HeadToHeadService
from services.team_form_service import TeamFormService


class DataExtractionCoordinator:
    """
    Coordinates the overall data extraction process.
    Manages service dependencies and orchestrates data extraction.
    """

    def __init__(
        self,
        browser: BaseBrowser,
        config: Config,
    ):
        """
        Initialize coordinator with browser and config.

        Args:
            browser: Browser instance for web interactions
            config: Configuration containing country, league, and rounds info
        """
        self.browser = browser
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize services
        self.team_factory = TeamFactory(browser)
        self.played_match_factory = PlayedMatchFactory(
            browser=self.browser,
            team_factory=self.team_factory,
        )
        self.team_form_service = TeamFormService(
            browser=browser,
            played_match_factory=self.played_match_factory,
            form_matches=5,
        )
        self.h2h_service = HeadToHeadService(
            browser=browser,
            played_match_factory=self.played_match_factory,
            max_matches=5,
        )
        self.fixture_match_factory = FixtureMatchFactory(
            browser=browser,
            team_factory=self.team_factory,
            team_form_service=self.team_form_service,
            h2h_service=self.h2h_service,
        )
        self.fixtures_url_factory = FixturesURLFactory(
            browser=browser,
            config=config,
        )

    def extract_fixtures_data(self) -> Tuple[List[FixtureMatch], Dict[str, List[str]]]:
        """
        Extract all fixture data according to configuration.

        Returns:
            Tuple of (list of FixtureMatch objects, dictionary of errors)
        """
        fixtures = []
        errors = {
            "fixture_urls": [],
            "fixture_matches": [],
        }

        try:
            # Step 1: Get fixture URLs
            self.logger.info(
                f"Extracting fixtures for {self.config.country} - {self.config.league}"
            )
            fixture_urls = self.fixtures_url_factory.get_fixtures_urls()

            if not fixture_urls:
                self.logger.error("No fixture URLs found")
                return [], errors

            self.logger.info(f"Found {len(fixture_urls)} fixtures to process")

            # Step 2: Process each fixture
            with tqdm(total=len(fixture_urls), desc="Processing fixtures") as pbar:
                for url in fixture_urls:
                    try:
                        fixture = self.fixture_match_factory.create_fixture_match(url)
                        if fixture:
                            fixtures.append(fixture)
                        else:
                            errors["fixture_matches"].append(
                                f"Failed to extract fixture from {url}"
                            )
                    except Exception as e:
                        self.logger.error(f"Error processing fixture {url}: {str(e)}")
                        errors["fixture_matches"].append(
                            f"Error processing {url}: {str(e)}"
                        )
                    finally:
                        pbar.update(1)
                        pbar.set_postfix({"successful": len(fixtures)})

            self.logger.info(
                f"Successfully extracted {len(fixtures)} out of {len(fixture_urls)} fixtures"
            )
            return fixtures, errors

        except Exception as e:
            self.logger.error(f"Error in extraction process: {str(e)}")
            return fixtures, errors
