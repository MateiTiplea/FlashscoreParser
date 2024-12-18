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
                self.logger.warning(
                    f"Failed to extract statistics for match: {match_url}; continuing without statistics"
                )

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
                statistics=statistics or None,
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
                self.logger.error(
                    "Statistics button not found. Cannot extract further statistics for match."
                )
                return False

            if "stats" not in stats_button.text.lower():
                self.logger.error(
                    "Invalid statistics button text. Cannot extract further statistics for match."
                )
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
                "expected_goals": None,
                "ball_possession": None,
                "goal_attempts": None,
                "shots_on_goal": None,
                "shots_off_goal": None,
                "blocked_shots": None,
                "big_chances": None,
                "corner_kicks": None,
                "shots_inside_box": None,
                "shots_outside_box": None,
                "hit_woodwork": None,
                "headed_goals": None,
                "goalkeeper_saves": None,
                "free_kicks": None,
                "offsides": None,
                "fouls": None,
                "yellow_cards": None,
                "red_cards": None,
                "throw_ins": None,
                "touches_in_opposition_box": None,
                "total_passes": None,
                "completed_passes": None,
                "total_passes_in_final_third": None,
                "completed_passes_in_final_third": None,
                "total_crosses": None,
                "completed_crosses": None,
                "total_tackles": None,
                "won_tackles": None,
                "clearances": None,
                "interceptions": None,
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
                "expected goals (xg)": ("expected_goals", float),
                "ball possession": ("ball_possession", self._parse_percentage),
                "goal attempts": ("goal_attempts", int),
                "shots on goal": ("shots_on_goal", int),
                "shots off goal": ("shots_off_goal", int),
                "blocked shots": ("blocked_shots", int),
                "big chances": ("big_chances", int),
                "corner kicks": ("corner_kicks", int),
                "shots inside the box": ("shots_inside_box", int),
                "shots outside the box": ("shots_outside_box", int),
                "hit the woodwork": ("hit_woodwork", int),
                "headed goals": ("headed_goals", int),
                "goalkeeper saves": ("goalkeeper_saves", int),
                "free kicks": ("free_kicks", int),
                "offsides": ("offsides", int),
                "fouls": ("fouls", int),
                "yellow cards": ("yellow_cards", int),
                "red cards": ("red_cards", int),
                "throw-ins": ("throw_ins", int),
                "touches in the opposition box": ("touches_in_opposition_box", int),
                "passes": (
                    "total_passes",
                    "completed_passes",
                    self._process_compound_stat,
                ),
                "passes in the final third": (
                    "total_passes_in_final_third",
                    "completed_passes_in_final_third",
                    self._process_compound_stat,
                ),
                "crosses": (
                    "total_crosses",
                    "completed_crosses",
                    self._process_compound_stat,
                ),
                "tackles": (
                    "total_tackles",
                    "won_tackles",
                    self._process_compound_stat,
                ),
                "clearances total": ("clearances", int),
                "interceptions": ("interceptions", int),
            }

            if stat_name in mapping:
                if len(mapping[stat_name]) == 2:
                    total_key, converter = mapping[stat_name]
                else:
                    total_key, completed_key, converter = mapping[stat_name]
                try:
                    if converter == self._process_compound_stat:
                        home_total, home_completed = converter(home_value)
                        away_total, away_completed = converter(away_value)

                        stats_data[total_key] = {
                            "home": home_total,
                            "away": away_total,
                        }
                        stats_data[completed_key] = {
                            "home": home_completed,
                            "away": away_completed,
                        }
                    else:
                        stats_data[total_key] = {
                            "home": converter(home_value),
                            "away": converter(away_value),
                        }
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

    def _process_compound_stat(self, value: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Process compound statistics in format "XX% (N/M)" where N is completed and M is total.
        Example: "88% (522/592)" -> returns (592, 522) as (total, completed)

        Args:
            value: String containing compound stat (e.g., "88% (522/592)")

        Returns:
            Tuple of (total, completed) integers
        """
        try:
            # Extract content within parentheses and split on '/'
            start = value.find("(") + 1
            end = value.find(")")
            if start == -1 or end == -1:
                return None, None

            numbers = value[start:end].split("/")
            if len(numbers) != 2:
                return None, None

            completed = int(numbers[0].strip())
            total = int(numbers[1].strip())
            return total, completed

        except (ValueError, AttributeError, IndexError) as e:
            self.logger.warning(f"Failed to parse compound stat: {value}")
            return None, None
