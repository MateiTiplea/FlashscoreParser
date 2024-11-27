# Location: services/factories/match_factory.py

import logging
from datetime import datetime
from typing import Optional, Tuple

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

from browsers.base_browser import BaseBrowser, LocatorType
from models.match import Match
from models.match_status import MatchStatus
from models.team import Team


class MatchFactory:
    """
    Factory class responsible for extracting basic match information.
    Creates Match objects with common data needed by both fixtures and played matches.
    """

    # CSS Selectors as class constants
    TOURNAMENT_HEADER_XPATH = '//*[@id="detail"]/div[3]/div/span[3]'
    MATCH_DATE_SELECTOR = "div.duelParticipant > div.duelParticipant__startTime"
    HOME_TEAM_SELECTOR = "#detail > div.duelParticipant > div.duelParticipant__home"
    AWAY_TEAM_SELECTOR = "#detail > div.duelParticipant > div.duelParticipant__away"
    MATCH_STATUS_SELECTOR = '//*[@id="detail"]/div[4]/div[3]/div/div[2]/span'

    def __init__(self, browser: BaseBrowser):
        """
        Initialize the factory with required dependencies.

        Args:
            browser: Instance of BaseBrowser for web interactions
            team_factory: Instance of TeamFactory for creating Team objects
        """
        self.browser = browser
        self.logger = logging.getLogger(__name__)

    def create_match(self, match_url: str) -> Optional[Match]:
        """
        Create a Match object by extracting data from the match page.

        Args:
            match_url: URL of the match page to extract data from

        Returns:
            Match object if extraction successful, None otherwise

        Raises:
            WebDriverException: If there are issues with browser navigation
        """
        try:
            # Navigate to match page
            self.browser.open_url(match_url)

            # Extract all required components
            country, competition, round_info = (
                self._extract_country_and_competition_and_round()
            )
            self.logger.info(
                f"Country: {country}, Competition: {competition}, Round: {round_info}"
            )
            match_date = self._extract_match_date()
            self.logger.info(f"Match Date: {match_date}")
            status = self._extract_match_status()
            self.logger.info(f"Match Status: {status}")
            home_team = self._extract_home_team()
            self.logger.info(f"Home Team: {home_team}")
            away_team = self._extract_away_team()
            self.logger.info(f"Away Team: {away_team}")

            # Verify we have all required data
            if not all([country, competition, match_date, home_team, away_team]):
                self.logger.error(f"Missing required match data for URL: {match_url}")
                return None

            # Create and return Match object
            return Match.create(
                match_url=match_url,
                country=country,
                competition=competition,
                match_date=match_date,
                round=round_info,
                home_team=home_team,
                away_team=away_team,
                status=status,
            )
        except WebDriverException as e:
            self.logger.error(f"Browser automation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating match object: {str(e)}")
            return None

    def _extract_country_and_competition_and_round(self) -> Tuple[str, str, str]:
        """
        Extract country and competition name, as well as round information from the match page.

        Returns:
            Tuple of (country, competition, round) information
        """
        try:
            element = self.browser.find_element(
                LocatorType.XPATH, self.TOURNAMENT_HEADER_XPATH
            )
            if not element:
                return ("", "", "")

            text = element.text
            parts = text.rsplit(" - ", maxsplit=1)
            if len(parts) == 2:
                country, competition = parts[0].split(": ")
                return (country.strip(), competition.strip(), parts[1].strip())
            else:
                return ("", "", "")
        except Exception as e:
            self.logger.error(f"Error extracting country/competition: {str(e)}")
            return ("", "", "")

    def _extract_match_date(self) -> Optional[datetime]:
        """
        Extract and parse match date from the page.

        Returns:
            datetime object if parsing successful, None otherwise
        """
        try:
            element = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.MATCH_DATE_SELECTOR
            )
            if not element:
                return None

            #  the format is dd.mm.yyyy hh:mm
            date_str = element.text
            return datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        except Exception as e:
            self.logger.error(f"Error extracting match date: {str(e)}")
            return None

    def _extract_match_status(self) -> MatchStatus:
        """
        Extract match status from the page.

        Returns:
            MatchStatus enum value
        """
        try:
            status_element = self.browser.find_element(
                LocatorType.XPATH, self.MATCH_STATUS_SELECTOR
            )
            if not status_element:
                return MatchStatus.SCHEDULED

            status_text = status_element.text
            if status_text.lower() == "finished":
                return MatchStatus.FINISHED
            else:
                return MatchStatus.SCHEDULED
        except Exception:
            return MatchStatus.SCHEDULED

    def is_fixture_match(self) -> bool:
        """
        Determine if the current match is a fixture (upcoming match).

        Returns:
            True if match is a fixture, False if it's a played match
        """
        try:
            status = self._extract_match_status()
            return status == MatchStatus.SCHEDULED
        except Exception:
            return False

    def _extract_home_team(self) -> Optional[Team]:
        """
        Extract home team information and create Team object.

        Returns:
            Team object if extraction successful, None otherwise
        """
        try:
            element = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.HOME_TEAM_SELECTOR
            )
            if not element:
                return None

            team_name = element.text
            team_url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            if not team_url:
                return None
            if not team_name:
                return None
            return Team.create(name=team_name, team_url=team_url)
        except Exception as e:
            self.logger.error(f"Error extracting home team: {str(e)}")
            return None

    def _extract_away_team(self) -> Optional[Team]:
        """
        Extract away team information and create Team object.

        Returns:
            Team object if extraction successful, None otherwise
        """
        try:
            element = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.AWAY_TEAM_SELECTOR
            )
            if not element:
                return None

            team_name = element.text
            team_url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            if not team_url:
                return None
            if not team_name:
                return None
            return Team.create(name=team_name, team_url=team_url)
        except Exception as e:
            self.logger.error(f"Error extracting away team: {str(e)}")
            return None
