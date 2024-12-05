# Location: services/team_form_service.py

import time
from typing import List, Optional

from browsers.base_browser import BaseBrowser, LocatorType
from logging_config import get_logger
from models.team import Team
from models.team_form import TeamForm
from services.factories.played_match_factory import PlayedMatchFactory


class TeamFormService:
    """Service for extracting recent form data for a team."""

    # CSS Selectors
    TEAM_RESULTS_WRAPPER_DIV = "#live-table > div.event.event--results > div"
    MATCHES_TABLE_DIV = "#live-table > div.event.event--results > div > div"
    MATCH_ROW_SELECTOR = "div[class^='event__match']"
    SHOW_MORE_BUTTON_SELECTOR = "a.event__more"

    def __init__(
        self,
        browser: BaseBrowser,
        played_match_factory: PlayedMatchFactory,
        form_matches: int = 5,
    ):
        """
        Initialize the service.

        Args:
            browser: Browser instance for web interactions
            played_match_factory: Factory for creating PlayedMatch objects
            form_matches: Number of recent matches to include in form (default: 5)
        """
        self.browser = browser
        self.played_match_factory = played_match_factory
        self.form_matches = form_matches
        self.logger = get_logger(__name__)

    def get_team_form(self, team: Team) -> Optional[TeamForm]:
        """
        Get recent form data for a team from their match history.

        Args:
            match_url: URL of the current match page
            team: Team object to get form for

        Returns:
            TeamForm object if extraction successful, None otherwise
        """
        try:
            # Save current window handle
            main_window = self.browser.driver.current_window_handle

            # Navigate to team's results page
            if not self._navigate_to_team_page(team):
                return None

            # Extract match URLs
            match_urls = self._extract_match_urls(main_window)
            if not match_urls:
                return None

            # Create played match objects
            matches = []
            for url in match_urls[: self.form_matches]:
                match = self.played_match_factory.create_played_match(url)
                if match:
                    matches.append(match)

            if not matches:
                return None

            # Create and return TeamForm object
            return TeamForm.create(team=team, matches=matches)

        except Exception as e:
            self.logger.error(f"Error getting form for team {team.name}: {str(e)}")
            return None

    def _navigate_to_team_page(self, team: Team) -> bool:
        """
        Navigate directly to team's results page.

        Args:
            team: Team object containing the team URL

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            results_url = f"{team.team_url}results/"
            self.browser.open_url(results_url)

            # Verify matches list is loaded
            matches_list = self.browser.find_element(
                LocatorType.CSS_SELECTOR,
                self.TEAM_RESULTS_WRAPPER_DIV,
                # suppress_exception=True,
            )
            return matches_list is not None

        except Exception as e:
            self.logger.error(f"Error navigating to team results page: {str(e)}")
            return False

    def _extract_match_urls(self, main_window) -> List[str]:
        """
        Extract URLs for recent matches from the results page.

        Args:
            main_window: Handle of the main window

        Returns:
            List of match URLs
        """
        match_urls = []
        try:
            # Find matches table
            matches_table = self.browser.find_element(
                LocatorType.CSS_SELECTOR,
                self.MATCHES_TABLE_DIV,
                # suppress_exception=True,
            )

            if not matches_table:
                self.logger.error("Matches table not found")
                return []

            # Load enough matches to get our required form history
            self._load_more_matches(matches_table)

            # Extract match rows
            rows = matches_table.find_elements(
                by=LocatorType.CSS_SELECTOR.value, value=self.MATCH_ROW_SELECTOR
            )

            # Process each row until we have enough matches
            for row in rows:
                if len(match_urls) >= self.form_matches:
                    break

                try:
                    # Get match URL directly from the row's link
                    match_link = row.find_element(
                        by=LocatorType.CSS_SELECTOR.value, value="a.eventRowLink"
                    )
                    if match_link:
                        match_url = match_link.get_attribute("href")
                        if match_url:
                            match_urls.append(match_url)

                except Exception as e:
                    self.logger.debug(f"Error processing match row: {str(e)}")
                    continue

            return match_urls

        except Exception as e:
            self.logger.error(f"Error extracting match URLs: {str(e)}")
            return []

    def _load_more_matches(self, table) -> None:
        """
        Click 'Show more' button to load additional matches if available.

        Args:
            table: WebElement of the matches table
        """
        try:
            while len(self._get_visible_matches()) < self.form_matches:
                if not self._check_show_more_button_exists(table):
                    self.logger.info("No more 'show more' button found")
                    break

                if not self._click_show_more_button(table):
                    self.logger.warning("Failed to load more matches")
                    break

                time.sleep(1)  # Small wait for content to load

        except Exception as e:
            self.logger.debug(f"Error loading more matches: {str(e)}")

    def _check_show_more_button_exists(self, table) -> bool:
        """
        Check if the "Show more" button exists and is interactable on the table.

        Args:
            table: WebElement of the matches table

        Returns:
            True if the button exists and is interactable, False otherwise
        """
        try:
            show_more = table.find_element(
                by=LocatorType.CSS_SELECTOR.value, value=self.SHOW_MORE_BUTTON_SELECTOR
            )

            if not show_more:
                return False

            return (
                show_more.is_displayed()
                and show_more.is_enabled()
                and "event__more--disable" not in show_more.get_attribute("class")
            )

        except Exception as e:
            self.logger.debug(f"Show more button not found: {str(e)}")
            return False

    def _click_show_more_button(self, table) -> bool:
        """
        Click the "Show more" button with success verification.

        Args:
            table: WebElement of the matches table

        Returns:
            True if button clicked successfully and new content loaded, False otherwise
        """
        try:
            show_more = table.find_element(
                by=LocatorType.CSS_SELECTOR.value, value=self.SHOW_MORE_BUTTON_SELECTOR
            )

            if not show_more:
                return False

            # Scroll to button
            self.browser.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                show_more,
            )

            time.sleep(0.5)  # Small wait for scroll completion
            show_more.click()
            return True

        except Exception as e:
            self.logger.error(f"Error clicking show more button: {str(e)}")
            return False

    def _get_visible_matches(self) -> List[str]:
        """Get list of currently visible match elements."""
        try:
            matches = self.browser.find_elements(
                LocatorType.CSS_SELECTOR,
                self.MATCH_ROW_SELECTOR,
                # suppress_exception=True,
            )
            return matches or []
        except Exception:
            return []
