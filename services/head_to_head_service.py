# Location: services/head_to_head_service.py

import logging
import time
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from browsers.base_browser import BaseBrowser, LocatorType
from models.head_to_head import HeadToHead
from models.team import Team
from services.factories.played_match_factory import PlayedMatchFactory


class HeadToHeadService:
    """Service for extracting head-to-head match history from a match page."""

    # CSS Selectors
    H2H_PAGE_BUTTON_SELECTOR = (
        "#detail > div.detailOver > div > a:nth-child(3) > button"
    )
    MATCH_LIST_SELECTOR = "#detail > div.h2hSection > div.h2h > div:nth-child(3)"
    H2H_ENCAPSULATED_SELECTOR = (
        "#detail > div.h2hSection > div.h2h > div:nth-child(3) > div.rows"
    )
    MATCH_ROW_SELECTOR = "div.h2h__row"
    SHOW_MORE_BUTTON_SELECTOR = (
        "#detail > div.h2hSection > div.h2h > div:nth-child(3) > div.showMore"
    )

    def __init__(
        self,
        browser: BaseBrowser,
        played_match_factory: PlayedMatchFactory,
        max_matches: int = 5,
    ):
        """
        Initialize the service.

        Args:
            browser: Browser instance for web interactions
            played_match_factory: Factory for creating PlayedMatch objects
            max_matches: Maximum number of H2H matches to extract (default: 5)
        """
        self.browser = browser
        self.played_match_factory = played_match_factory
        self.max_matches = max_matches
        self.logger = logging.getLogger(__name__)

    def get_head_to_head(
        self, match_url: str, team_a: Team, team_b: Team
    ) -> Optional[HeadToHead]:
        """
        Get head-to-head record between two teams from a match page.

        Args:
            match_url: URL of the match page containing H2H data
            team_a: First team
            team_b: Second team

        Returns:
            HeadToHead object if extraction successful, None otherwise
        """
        try:
            # Save current window handle
            main_window = self.browser.driver.current_window_handle

            # Navigate to base match page
            if self.browser.save_current_url() != match_url:
                self.browser.open_url(match_url)

            # Switch to H2H tab
            if not self._navigate_to_h2h_tab():
                return None

            # Extract H2H match URLs
            match_urls = self._extract_h2h_match_urls(main_window)
            if not match_urls:
                return None

            # Create played match objects
            matches = []
            for url in match_urls[: self.max_matches]:
                match = self.played_match_factory.create_played_match(url)
                if match:
                    matches.append(match)

            if not matches:
                return None

            # Create and return H2H object
            return HeadToHead.create(team_a=team_a, team_b=team_b, matches=matches)

        except Exception as e:
            self.logger.error(
                f"Error getting H2H for {team_a.name} vs {team_b.name}: {str(e)}"
            )
            return None

    def _navigate_to_h2h_tab(self) -> bool:
        """
        Switch to the H2H tab on the match page.

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            # Click on H2H tab
            if not self.browser.click_element(
                LocatorType.CSS_SELECTOR,
                self.H2H_PAGE_BUTTON_SELECTOR,
                suppress_exception=True,
            ):
                return False

            # Verify H2H section is loaded
            h2h_section = self.browser.find_element(
                LocatorType.CSS_SELECTOR,
                self.MATCH_LIST_SELECTOR,
                suppress_exception=True,
            )
            return h2h_section is not None

        except Exception as e:
            self.logger.error(f"Error navigating to H2H tab: {str(e)}")
            return False

    def _click_row_and_get_url(self, row, main_window) -> Optional[str]:
        """
        Click a H2H row and get the URL from the new window.

        Args:
            row: WebElement of the H2H row
            main_window: Handle of the main window

        Returns:
            URL of the match detail page or None if unsuccessful
        """
        try:
            # Get initial window handles
            initial_handles = set(self.browser.driver.window_handles)

            # Click the row
            self.browser.driver.execute_script("arguments[0].click();", row)

            # Wait for new window
            WebDriverWait(self.browser.driver, 10).until(
                lambda driver: len(driver.window_handles) > len(initial_handles)
            )

            # Get new window handle
            new_handles = set(self.browser.driver.window_handles) - initial_handles
            if not new_handles:
                return None

            new_window = new_handles.pop()

            # Switch to new window
            self.browser.driver.switch_to.window(new_window)

            # Get URL
            url = self.browser.driver.current_url

            # Close new window and switch back
            self.browser.driver.close()
            self.browser.driver.switch_to.window(main_window)

            return url
        except Exception as e:
            self.logger.debug(f"Error getting URL from row click: {str(e)}")
            # Make sure we switch back to main window
            try:
                self.browser.driver.switch_to.window(main_window)
            except:
                pass
            return None

    def _extract_h2h_match_urls(self, main_window) -> List[str]:
        """Extract URLs for H2H matches from the match page."""
        match_urls = []
        try:
            # Find all H2H rows
            rows = self.browser.find_elements(
                LocatorType.CSS_SELECTOR,
                f"{self.H2H_ENCAPSULATED_SELECTOR} > {self.MATCH_ROW_SELECTOR}",
                suppress_exception=True,
            )

            for row in rows:
                try:
                    # Click row and get URL
                    url = self._click_row_and_get_url(row, main_window)
                    if url:
                        match_urls.append(url)
                except Exception as e:
                    self.logger.debug(f"Error processing H2H row: {str(e)}")
                    continue

            return match_urls

        except Exception as e:
            self.logger.error(f"Error extracting H2H match URLs: {str(e)}")
            return []

    def _load_more_matches(self) -> None:
        """
        Click 'Show more' button to load additional matches if available.
        """
        try:
            while len(self._get_visible_matches()) < self.max_matches:
                show_more = self.browser.find_element(
                    LocatorType.CSS_SELECTOR,
                    self.SHOW_MORE_BUTTON_SELECTOR,
                    suppress_exception=True,
                )
                if not show_more or not show_more.is_displayed():
                    break

                # Click show more button
                if not self.browser.click_element(
                    LocatorType.CSS_SELECTOR,
                    self.SHOW_MORE_BUTTON_SELECTOR,
                    suppress_exception=True,
                ):
                    break

        except Exception as e:
            self.logger.debug(f"Error loading more matches: {str(e)}")

    def _get_visible_matches(self) -> List[str]:
        """Get currently visible match URLs."""
        try:
            matches = self.browser.find_elements(
                LocatorType.CSS_SELECTOR,
                f"{self.H2H_ENCAPSULATED_SELECTOR} > {self.MATCH_ROW_SELECTOR}",
                suppress_exception=True,
            )
            return matches or []
        except Exception:
            return []
