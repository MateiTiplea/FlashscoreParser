# Location: services/factories/fixtures_url_factory.py

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from browsers.base_browser import BaseBrowser, LocatorType
from models.config import Config


class FixturesURLFactory:
    """
    Factory class responsible for extracting fixture URLs based on configuration.
    Takes a Config instance and extracts URLs for the specified league and rounds.
    """

    MAPPINGS_DIR = Path(__file__).parent.parent.parent / "mappings"
    LEAGUES_MAPPING_FILE = MAPPINGS_DIR / "leagues_url_mapping.json"
    FIXTURES_PATH_SUFFIX = "fixtures/"

    # CSS Selectors as class constants
    FIXTURES_TABLE_SELECTOR = "#live-table > div.event.event--fixtures > div > div"
    SHOW_MORE_BUTTON_SELECTOR = "a.event__more"
    EVENT_ROUND_SELECTOR = "div.event__round"
    EVENT_MATCH_SELECTOR = "div.event__match"
    MATCH_LINK_SELECTOR = "a.eventRowLink"
    COOKIE_CONSENT_SELECTOR = "#onetrust-accept-btn-handler"

    def __init__(self, browser: BaseBrowser, config: Config):
        """
        Initialize the factory with a browser instance and configuration.

        Args:
            browser: Instance of BaseBrowser to use for navigation
            config: Configuration instance containing country, league, and rounds info

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If mapping file doesn't exist
        """
        self.browser = browser
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.league_url_mapping = self._load_league_mapping()

        if not self._validate_config():
            raise ValueError(
                f"Invalid configuration: country='{config.country}', league='{config.league}'"
            )

    def _validate_config(self) -> bool:
        """
        Validate that the provided configuration matches available mappings.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        return (
            self.config.country in self.league_url_mapping
            and self.config.league in self.league_url_mapping[self.config.country]
        )

    def _load_league_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Load the league URL mapping from the JSON file.

        Returns:
            Dictionary containing league URLs by country and league name

        Raises:
            FileNotFoundError: If the mapping file doesn't exist
            JSONDecodeError: If the mapping file is invalid
        """
        if not self.LEAGUES_MAPPING_FILE.exists():
            raise FileNotFoundError(
                f"League mapping file not found at {self.LEAGUES_MAPPING_FILE}"
            )

        try:
            with open(self.LEAGUES_MAPPING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding league mapping file: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading league mapping file: {str(e)}")
            raise

    def get_fixtures_urls(self) -> List[str]:
        """
        Get list of fixture URLs based on configuration.

        Returns:
            List of URLs for fixtures matching the configuration

        Raises:
            WebDriverException: If there are issues with browser navigation
        """
        base_url = self._get_base_league_url()
        if not base_url:
            return []

        try:
            if not self._navigate_to_fixtures_section(base_url):
                return []

            if not self._handle_cookie_consent():
                self.logger.warning(
                    "Cookie consent handling failed, attempting to continue"
                )

            time.sleep(2)  # Small wait for page to load

            fixtures_table = self._find_fixtures_table()
            if not fixtures_table:
                return []

            # Load required number of rounds
            rounds_loaded = self._load_rounds(fixtures_table)
            if rounds_loaded < self.config.rounds:
                self.logger.warning(
                    f"Could only load {rounds_loaded} rounds out of {self.config.rounds} requested"
                )

            return self._extract_fixture_urls()

        except WebDriverException as e:
            self.logger.error(f"Browser automation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while extracting fixture URLs: {str(e)}"
            )
            return []

    def _get_base_league_url(self) -> Optional[str]:
        """
        Get the base URL for the configured league.

        Returns:
            Base URL for the league or None if not found
        """
        try:
            return self.league_url_mapping[self.config.country][self.config.league]
        except KeyError:
            self.logger.error(
                f"League URL not found for {self.config.league} in {self.config.country}"
            )
            return None

    def _extract_fixture_urls(self) -> List[str]:
        """
        Extract fixture URLs from the league page for specified rounds.

        Returns:
            List of fixture URLs
        """
        try:
            fixtures_table = self._find_fixtures_table()
            if not fixtures_table:
                return []

            matches_urls = []
            parsed_rounds = 0
            current_round_matches: List[str] = []

            blocks = fixtures_table.find_elements(
                by=LocatorType.CSS_SELECTOR.value,
                value=f"{self.EVENT_ROUND_SELECTOR}, {self.EVENT_MATCH_SELECTOR}",
            )
            self.logger.info(f"Found {len(blocks)} blocks in fixtures table")
            for block in blocks:
                class_attr = block.get_attribute("class")

                if "event__round" in class_attr:
                    if parsed_rounds >= self.config.rounds:
                        break
                    if current_round_matches:  # Add previous round's matches
                        matches_urls.extend(current_round_matches)
                        current_round_matches = []
                    parsed_rounds += 1

                elif (
                    "event__match" in class_attr and parsed_rounds <= self.config.rounds
                ):
                    try:
                        match_url = block.find_element(
                            by=LocatorType.CSS_SELECTOR.value,
                            value=self.MATCH_LINK_SELECTOR,
                        ).get_attribute("href")
                        current_round_matches.append(match_url)
                    except Exception as e:
                        self.logger.warning(f"Failed to extract match URL: {str(e)}")
                        continue

            # Add the last round's matches
            if current_round_matches and parsed_rounds <= self.config.rounds:
                matches_urls.extend(current_round_matches)

            self.logger.info(
                f"Extracted {len(matches_urls)} match URLs from {parsed_rounds} rounds"
            )
            return matches_urls

        except Exception as e:
            self.logger.error(f"Error extracting fixture URLs: {str(e)}")
            return []

    def _navigate_to_fixtures_section(self, base_url: str) -> bool:
        """
        Navigate to the fixtures section of the league page.

        Returns:
            True if navigation successful, False otherwise
        """
        fixtures_url = f"{base_url}{self.FIXTURES_PATH_SUFFIX}"
        try:
            self.browser.open_url(fixtures_url)
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to fixtures URL: {str(e)}")
            return False

    def _handle_cookie_consent(self) -> bool:
        """
        Handle any cookie consent popups.

        Returns:
            True if handled successfully or not present, False if failed
        """
        possible_cookie_selector = "#onetrust-accept-btn-handler"
        if not self.browser.is_element_present(
            LocatorType.CSS_SELECTOR, possible_cookie_selector, suppress_exception=True
        ):
            return True

        try:
            self.browser.click_element(
                LocatorType.CSS_SELECTOR, possible_cookie_selector
            )
            return True
        except Exception as e:
            self.logger.error(f"Error handling cookie consent: {str(e)}")
            return False

    def _find_fixtures_table(self) -> Optional[WebElement]:
        """
        Find the table element containing fixtures.

        Returns:
            WebElement of the table or None if not found
        """
        fixtures_table_css_locator = (
            "#live-table > div.event.event--fixtures > div > div"
        )
        if not self.browser.is_element_present(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value=fixtures_table_css_locator,
            suppress_exception=True,
        ):
            self.logger.error("Fixtures table not found on the page")
            return None

        return self.browser.find_element(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value=fixtures_table_css_locator,
            suppress_exception=True,
        )

    def _check_show_more_button_exists(self, table: WebElement) -> bool:
        """
        Check if the "Show more" button exists and is interactable on the fixtures table.

        Args:
            table: WebElement of the fixtures table

        Returns:
            True if the button exists and is interactable, False otherwise
        """
        try:
            # First check if button exists in DOM
            show_more = table.find_element(
                by=LocatorType.CSS_SELECTOR.value, value=self.SHOW_MORE_BUTTON_SELECTOR
            )

            if not show_more:
                return False

            # Check if button is visible and enabled
            return (
                show_more.is_displayed()
                and show_more.is_enabled()
                and "event__more--disable" not in show_more.get_attribute("class")
            )

        except Exception as e:
            self.logger.debug(f"Show more button not found: {str(e)}")
            return False

    def _click_show_more_button(self, table: WebElement) -> bool:
        """
        Click the "Show more" button with improved success verification.

        Args:
            table: WebElement of the fixtures table

        Returns:
            True if the button was clicked successfully and new content loaded, False otherwise
        """
        try:
            # Get initial state
            initial_content = self._get_current_content_state(table)

            # Find and click the button
            show_more = WebDriverWait(table, 10).until(
                EC.element_to_be_clickable(
                    (LocatorType.CSS_SELECTOR.value, self.SHOW_MORE_BUTTON_SELECTOR)
                )
            )

            if not show_more:
                return False

            # Scroll to button
            self.browser.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                show_more,
            )

            # Small wait for scroll completion
            time.sleep(0.5)

            # Click the button
            show_more.click()

            # Wait and verify that new content was loaded
            return self._verify_content_changed(table, initial_content)

        except Exception as e:
            self.logger.error(f"Error while clicking show more button: {str(e)}")
            return False

    def _get_current_content_state(self, table: WebElement) -> dict:
        """
        Get current state of the content for comparison.

        Args:
            table: WebElement of the fixtures table

        Returns:
            dict containing current content state metrics
        """
        try:
            return {
                "rounds_count": len(
                    table.find_elements(
                        by=LocatorType.CSS_SELECTOR.value, value="div.event__round"
                    )
                ),
                "matches_count": len(
                    table.find_elements(
                        by=LocatorType.CSS_SELECTOR.value, value="div.event__match"
                    )
                ),
                "last_round_text": (
                    table.find_elements(
                        by=LocatorType.CSS_SELECTOR.value, value="div.event__round"
                    )[-1].text
                    if table.find_elements(
                        by=LocatorType.CSS_SELECTOR.value, value="div.event__round"
                    )
                    else None
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error getting content state: {str(e)}")
            return {}

    def _verify_content_changed(
        self, table: WebElement, initial_state: dict, timeout: int = 5
    ) -> bool:
        """
        Verify that the content actually changed after clicking the button.

        Args:
            table: WebElement of the fixtures table
            initial_state: State before clicking
            timeout: Maximum time to wait for changes

        Returns:
            bool indicating whether content changed
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_state = self._get_current_content_state(table)

                # Check if content increased
                if current_state.get("rounds_count", 0) > initial_state.get(
                    "rounds_count", 0
                ) or current_state.get("matches_count", 0) > initial_state.get(
                    "matches_count", 0
                ):
                    self.logger.info(
                        "Content successfully loaded after clicking show more"
                    )
                    return True

                # Check if button is now disabled (might indicate no more content)
                disabled_button = table.find_elements(
                    by=LocatorType.CSS_SELECTOR.value,
                    value=f"{self.SHOW_MORE_BUTTON_SELECTOR}.event__more--disable",
                )
                if disabled_button:
                    self.logger.info(
                        "Show more button is now disabled - no more content to load"
                    )
                    return True

                time.sleep(0.5)  # Short pause before next check

            self.logger.warning("Content did not change after clicking show more")
            return False

        except Exception as e:
            self.logger.error(f"Error verifying content change: {str(e)}")
            return False

    def _get_visible_rounds_number(self, table: WebElement) -> int:
        """
        Get the number of visible rounds in the fixtures table.

        Args:
            table: WebElement of the fixtures table

        Returns:
            Number of visible rounds
        """
        try:
            rounds = table.find_elements(
                by=LocatorType.CSS_SELECTOR.value, value="div.event__round"
            )
            return len(rounds)
        except Exception as e:
            self.logger.error(f"Error getting visible rounds: {str(e)}")
            return 0

    def _load_rounds(self, table: WebElement) -> int:
        """
        Load all possible rounds in the fixtures table.

        Args:
            table: WebElement of the fixtures table

        Returns:
            Number of visible rounds after loading
        """
        rounds_to_process = self.config.rounds
        visible_rounds = self._get_visible_rounds_number(table)
        attempts = 0
        max_attempts = 10

        while visible_rounds < rounds_to_process + 1 and attempts < max_attempts:
            if not self._check_show_more_button_exists(table):
                self.logger.info("No more 'show more' button found")
                break

            initial_rounds = visible_rounds

            if not self._click_show_more_button(table):
                self.logger.warning(
                    f"Failed to load more rounds at attempt {attempts + 1}"
                )
                break

            # Get new count after successful click
            visible_rounds = self._get_visible_rounds_number(table)

            # Check if we actually got new content
            if visible_rounds <= initial_rounds:
                self.logger.warning("No new rounds loaded despite successful click")
                break

            self.logger.info(
                f"Successfully loaded rounds: {visible_rounds} of {rounds_to_process}"
            )
            attempts += 1

        return visible_rounds
