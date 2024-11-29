import logging
from typing import Optional

from selenium.common.exceptions import WebDriverException

from browsers.base_browser import BaseBrowser, LocatorType
from models.team import Team


class TeamFactory:
    """Factory class responsible for creating Team instances with full details."""

    # CSS Selectors
    TEAM_NAME_SELECTOR = '//*[@id="mc"]/div[5]/div[1]/div[2]/div[1]/div[1]'
    COUNTRY_SELECTOR = '//*[@id="mc"]/div[5]/div[1]/h2/a[2]'
    STADIUM_INFO_SELECTOR = '//*[@id="mc"]/div[5]/div[1]/div[2]/div[2]'

    def __init__(self, browser: BaseBrowser):
        """Initialize the factory with a browser instance."""
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def create_team_with_context(
        self, team_url: str, return_url: str
    ) -> Optional[Team]:
        """
        Create a Team instance with full details from the team's page while preserving browser context.

        Args:
            team_url: URL of the team's page
            return_url: URL to return to after extracting data

        Returns:
            Team object if extraction successful, None otherwise
        """
        try:
            team = self.create_team(team_url)
            self.browser.restore_url(return_url)
            return team
        except Exception as e:
            self.logger.error(f"Error creating team object with context: {str(e)}")
            self.browser.restore_url(return_url)
            return None

    def create_team(self, team_url: str) -> Optional[Team]:
        """
        Create a Team instance with full details from the team's page.

        Args:
            team_url: URL of the team's page

        Returns:
            Team object if extraction successful, None otherwise
        """
        try:
            self.browser.open_url(team_url)

            # Extract basic info
            name = self._extract_team_name()
            country = self._extract_country()
            stadium, city, capacity = self._extract_stadium_info()

            if not name:
                self.logger.error(f"Could not extract team name from {team_url}")
                return None

            return Team.create(
                name=name,
                team_url=team_url,
                country=country,
                stadium=stadium,
                stadium_city=city,
                capacity=capacity,
            )

        except WebDriverException as e:
            self.logger.error(f"Browser automation error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating team object: {str(e)}")
            return None

    def _extract_team_name(self) -> Optional[str]:
        """Extract team name from the page."""
        element = self.browser.find_element(
            LocatorType.XPATH, self.TEAM_NAME_SELECTOR, suppress_exception=True
        )
        return element.text if element else None

    def _extract_country(self) -> Optional[str]:
        """Extract team's country from the page."""
        element = self.browser.find_element(
            LocatorType.XPATH, self.COUNTRY_SELECTOR, suppress_exception=True
        )
        return element.text.title() if element else None

    def _extract_stadium_info(
        self,
    ) -> tuple[Optional[str], Optional[str], Optional[int]]:
        """Extract stadium information from the page."""
        element = self.browser.find_element(
            LocatorType.XPATH,
            self.STADIUM_INFO_SELECTOR,
            suppress_exception=True,
        )
        if not element:
            return None, None, None

        try:
            lines = element.text.split("\n")
            stadium_line = lines[0].split(":")
            stadium = stadium_line[1].strip().split(" (")[0].strip()
            city = stadium_line[1].strip().split(" (")[1][:-1].strip()
            capacity_line = lines[1].split(":")
            capacity = int(capacity_line[1].replace(" ", ""))
            return stadium, city, capacity
        except Exception as e:
            self.logger.error(f"Error extracting stadium info: {str(e)}")
            return None, None, None
