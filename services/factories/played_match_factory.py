# Location: services/factories/played_match_factory.py

import time
from typing import Optional, Tuple

from selenium.common.exceptions import TimeoutException, WebDriverException

from browsers.base_browser import BaseBrowser, LocatorType
from logging_config import get_logger
from models.match_statistics import MatchStatistics
from models.played_match import PlayedMatch
from services.factories.match_factory import MatchFactory
from services.factories.team_factory import TeamFactory


class PlayedMatchFactory(MatchFactory):
    """
    Factory class for creating PlayedMatch objects.
    Extends MatchFactory to add score and statistics extraction.
    """

    # CSS Selectors for match scores
    SCORE_SELECTOR = "#detail > div.duelParticipant > div.duelParticipant__score"
    HOME_SCORE_SELECTOR = "#detail > div.duelParticipant > div.duelParticipant__score > div > div.detailScore__wrapper > span:nth-child(1)"
    AWAY_SCORE_SELECTOR = "#detail > div.duelParticipant > div.duelParticipant__score > div > div.detailScore__wrapper > span:nth-child(3)"

    # CSS Selectors for statistics
    STATS_BUTTON_SELECTOR = (
        "#detail > div.filterOver.filterOver--indent > div > a:nth-child(2) > button"
    )
    STATS_CONTAINER_SELECTOR = "#detail > div.section"

    def __init__(self, browser: BaseBrowser, team_factory: TeamFactory):
        """Initialize with browser and team factory instances."""
        super().__init__(browser, team_factory)
        self.logger = get_logger(__name__)

    def create_played_match(self, match_url: str) -> Optional[PlayedMatch]:
        """
        Create a PlayedMatch object by extracting all match data.

        Args:
            match_url: URL of the match page

        Returns:
            PlayedMatch object if extraction successful, None otherwise
        """
        try:
            # Get base match data using parent class
            base_match = super().create_match(match_url)
            if not base_match:
                return None

            # Extract score
            home_score, away_score = self._extract_score()
            if home_score is None or away_score is None:
                self.logger.error(f"Failed to extract score for match: {match_url}")
                return None

            # Extract statistics
            statistics = self._extract_match_statistics(base_match.match_id)
            if not statistics:
                self.logger.error(
                    f"Failed to extract statistics for match: {match_url}"
                )
                return None

            # Create played match
            return PlayedMatch.create(
                match_url=match_url,
                country=base_match.country,
                competition=base_match.competition,
                match_date=base_match.match_date,
                round=base_match.round,
                home_team=base_match.home_team,
                away_team=base_match.away_team,
                home_score=home_score,
                away_score=away_score,
                statistics=statistics,
                status=base_match.status,
            )

        except Exception as e:
            self.logger.error(f"Error creating played match object: {str(e)}")
            return None

    def _extract_score(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Extract the final score from the match page.

        Returns:
            Tuple of (home_score, away_score)
        """
        try:
            home_score_element = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.HOME_SCORE_SELECTOR
            )
            away_score_element = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.AWAY_SCORE_SELECTOR
            )

            if not home_score_element or not away_score_element:
                return None, None

            try:
                home_score = int(home_score_element.text)
                away_score = int(away_score_element.text)
                return home_score, away_score
            except ValueError:
                self.logger.error("Failed to convert score text to integers")
                return None, None

        except Exception as e:
            self.logger.error(f"Error extracting match score: {str(e)}")
            return None, None

    def _navigate_to_statistics(self) -> bool:
        """
        Click the statistics button to show detailed match statistics.

        Returns:
            True if successful, False otherwise
        """
        try:
            stats_button = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.STATS_BUTTON_SELECTOR
            )
            if not stats_button:
                return False

            stats_button.click()
            time.sleep(1)
            return True
        except (TimeoutException, WebDriverException):
            self.logger.error("Failed to click statistics button")
            return False

    def _extract_match_statistics(self, match_id) -> Optional[MatchStatistics]:
        """
        Extract detailed match statistics.

        Args:
            match_id: UUID of the match

        Returns:
            MatchStatistics object if extraction successful, None otherwise
        """

        # Navigate to statistics tab
        if not self._navigate_to_statistics():
            return None

        try:
            stats_container = self.browser.find_element(
                LocatorType.CSS_SELECTOR, self.STATS_CONTAINER_SELECTOR
            )
            if not stats_container:
                return None

            # Initialize statistics dictionary
            stats_data = {
                "match_id": match_id,
                "home_expected_goals": None,
                "away_expected_goals": None,
                "home_possession": None,
                "away_possession": None,
                "home_shots_total": None,
                "away_shots_total": None,
                "home_shots_on_target": None,
                "away_shots_on_target": None,
                "home_shots_off_target": None,
                "away_shots_off_target": None,
                "home_shots_blocked": None,
                "away_shots_blocked": None,
                "home_free_kicks": None,
                "away_free_kicks": None,
                "home_corners": None,
                "away_corners": None,
                "home_offsides": None,
                "away_offsides": None,
                "home_throw_ins": None,
                "away_throw_ins": None,
                "home_goalkeeper_saves": None,
                "away_goalkeeper_saves": None,
                "home_fouls": None,
                "away_fouls": None,
                "home_yellow_cards": None,
                "away_yellow_cards": None,
                "home_red_cards": None,
                "away_red_cards": None,
                "home_total_passes": None,
                "away_total_passes": None,
                "home_completed_passes": None,
                "away_completed_passes": None,
                "home_crosses": None,
                "away_crosses": None,
                "home_interceptions": None,
                "away_interceptions": None,
            }

            # Extract all statistic rows
            stat_rows = stats_container.find_elements(
                by=LocatorType.CSS_SELECTOR.value, value="div[class^='wcl-row_']"
            )

            for row in stat_rows:
                self._process_stat_row(row, stats_data)

            return MatchStatistics.create(**stats_data)

        except Exception as e:
            self.logger.error(f"Error extracting match statistics: {str(e)}")
            return None

    def _process_stat_row(self, row, stats_data: dict) -> None:
        """
        Process a single statistics row and update the stats dictionary.

        Args:
            row: WebElement containing the statistic row
            stats_data: Dictionary to update with extracted values
        """
        try:
            # Extract values
            home_value = row.find_element(
                by=LocatorType.XPATH.value, value="div[1]/div[1]"
            ).text
            away_value = row.find_element(
                by=LocatorType.XPATH.value, value="div[1]/div[3]"
            ).text
            stat_name = row.find_element(
                by=LocatorType.XPATH.value, value="div[1]/div[2]"
            ).text.lower()

            # Map statistic name to dictionary keys
            mapping = {
                "expected goals (xg)": (
                    "home_expected_goals",
                    "away_expected_goals",
                    float,
                ),
                "ball possession": (
                    "home_possession",
                    "away_possession",
                    self._parse_percentage,
                ),
                "goal attempts": (
                    "home_shots_total",
                    "away_shots_total",
                    int,
                ),
                "shots on goal": (
                    "home_shots_on_target",
                    "away_shots_on_target",
                    int,
                ),
                "shots off goal": (
                    "home_shots_off_target",
                    "away_shots_off_target",
                    int,
                ),
                "blocked shots": (
                    "home_shots_blocked",
                    "away_shots_blocked",
                    int,
                ),
                "free kicks": (
                    "home_free_kicks",
                    "away_free_kicks",
                    int,
                ),
                "corner kicks": (
                    "home_corners",
                    "away_corners",
                    int,
                ),
                "offsides": (
                    "home_offsides",
                    "away_offsides",
                    int,
                ),
                "throw-ins": (
                    "home_throw_ins",
                    "away_throw_ins",
                    int,
                ),
                "goalkeeper saves": (
                    "home_goalkeeper_saves",
                    "away_goalkeeper_saves",
                    int,
                ),
                "fouls": (
                    "home_fouls",
                    "away_fouls",
                    int,
                ),
                "yellow cards": (
                    "home_yellow_cards",
                    "away_yellow_cards",
                    int,
                ),
                "red cards": (
                    "home_red_cards",
                    "away_red_cards",
                    int,
                ),
                "total passes": (
                    "home_total_passes",
                    "away_total_passes",
                    int,
                ),
                "completed passes": (
                    "home_completed_passes",
                    "away_completed_passes",
                    int,
                ),
                "crosses completed": (
                    "home_crosses",
                    "away_crosses",
                    int,
                ),
                "interceptions": (
                    "home_interceptions",
                    "away_interceptions",
                    int,
                ),
            }

            if stat_name in mapping:
                home_key, away_key, converter = mapping[stat_name]
                try:
                    stats_data[home_key] = converter(home_value)
                    stats_data[away_key] = converter(away_value)
                except (ValueError, TypeError):
                    self.logger.warning(
                        f"Failed to convert values for {stat_name}: {home_value}, {away_value}"
                    )
            else:
                self.logger.warning(f"Unknown statistic: {stat_name}")

        except Exception as e:
            self.logger.error(f"Error processing statistic row: {str(e)}")

    def _parse_percentage(self, value: str) -> Optional[int]:
        """
        Parse percentage value from string.

        Args:
            value: String containing percentage (e.g., "65%")

        Returns:
            Float value or None if parsing fails
        """
        try:
            return int(value.replace("%", ""))
        except (ValueError, AttributeError):
            return None
