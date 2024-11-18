import time
from typing import List

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from browsers.base_browser import BaseBrowser, LocatorType
from models.config import Config
from models.match import Match


def remove_cookie(browser: BaseBrowser) -> None:
    # remove the accept cookies from the page
    possible_cookie_selector = "#onetrust-accept-btn-handler"
    if browser.is_element_present(
        locator_type=LocatorType.CSS_SELECTOR,
        locator_value=possible_cookie_selector,
        timeout=2,  # Short timeout since we're trying multiple selectors
        suppress_exception=True,
    ):
        cookie_button = browser.find_element(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value=possible_cookie_selector,
            timeout=2,  # Short timeout since we're trying multiple selectors
            suppress_exception=True,
        )
        if cookie_button:
            browser.click_element(
                locator_type=LocatorType.CSS_SELECTOR,
                locator_value=possible_cookie_selector,
                suppress_exception=True,
            )
            # Wait for banner to disappear
            browser.wait_for_element_to_disappear(
                locator_type=LocatorType.ID,
                locator_value="#onetrust-banner-sdk",
                suppress_exception=True,
            )


def check_show_more_exists(matches_table: WebElement) -> bool:
    try:
        condition = EC.visibility_of_element_located(
            (LocatorType.CSS_SELECTOR.value, "a.event__more")
        )
        show_more = WebDriverWait(matches_table, 10).until(condition)
        print("Show more exists")
        return show_more is not None
    except:
        print("Show more does not exist")
        return False


def click_show_more(matches_table: WebElement) -> bool:
    try:
        condition = EC.visibility_of_element_located(
            (LocatorType.CSS_SELECTOR.value, "a.event__more")
        )
        show_more = WebDriverWait(matches_table, 10).until(condition)
        if show_more and show_more.is_enabled():
            show_more.click()
            print("Clicked show more success")
            return True
        else:
            print("Show more is not enabled")
            return False
    except:
        print("Failed to click show more")
        return False


def extract_matches(fixtures_table: WebElement, rounds_to_process: int) -> List[Match]:
    current_round = None
    parsed_rounds = 0
    blocks = None
    try:
        blocks = fixtures_table.find_elements(
            by=LocatorType.CSS_SELECTOR.value, value="div"
        )
    except Exception as e:
        print(f"Error while extracting matches: {str(e)}")
        return []

    matches = list()
    for block in blocks:
        try:
            if parsed_rounds > rounds_to_process:
                break
            if "event__round" in block.get_attribute("class"):
                current_round = block.text
                parsed_rounds += 1
            elif "event__match" in block.get_attribute("class"):
                match_date = block.find_element(
                    by=LocatorType.CSS_SELECTOR.value, value="div.event__time"
                ).text
                match_url = block.find_element(
                    by=LocatorType.CSS_SELECTOR.value, value="a.eventRowLink"
                ).get_attribute("href")
                home_team_name = block.find_element(
                    by=LocatorType.CSS_SELECTOR.value,
                    value="div.event__homeParticipant",
                ).text
                away_team_name = block.find_element(
                    by=LocatorType.CSS_SELECTOR.value,
                    value="div.event__awayParticipant",
                ).text
                match = Match(
                    match_url=match_url,
                    competition="",
                    home_team_name=home_team_name,
                    away_team_name=away_team_name,
                    match_date=match_date,
                    round=current_round,
                )
                matches.append(match)
        except Exception as e:
            print(f"Error while extracting matches: {str(e)}")
            continue

    return matches


class MatchFactory:
    def __init__(self, browser: BaseBrowser, config: Config):
        self.browser = browser
        self.config = config

    def get_visible_rounds_number(self, fixtures_table: WebElement) -> int:
        try:
            event_rounds = fixtures_table.find_elements(
                by=LocatorType.CLASS_NAME.value, value="event__round"
            )
            return len(event_rounds)
        except Exception as e:
            print(f"Error while extracting matches: {str(e)}")
            return 0

    def load_all_rounds(self, fixtures_table: WebElement) -> int:
        nr_rounds = self.get_visible_rounds_number(fixtures_table)
        while nr_rounds < self.config.rounds + 1:
            if not check_show_more_exists(fixtures_table):
                print("No more rounds to load")
                break
            if not click_show_more(fixtures_table):
                print("Failed to click show more")
                break
            time.sleep(5)
            nr_rounds = self.get_visible_rounds_number(fixtures_table)
        return nr_rounds

    def create_matches(self) -> List[Match]:
        """
        Extract and create Match objects for the maximum number of rounds specified in the Config
        using the browser instance and the configuration provided
        """
        matches = list()

        fixtures_url = f"{self.config.league_url}fixtures/"
        #  Navigate to the fixtures URL for the given league
        self.browser.open_url(fixtures_url)
        remove_cookie(self.browser)
        #  TODO: implement match extraction logic

        #  First step: retrieve the table element that contains all match rows
        fixtures_table = None
        if self.browser.is_element_present(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value="#live-table > div.event.event--fixtures > div > div",
            suppress_exception=True,
        ):
            fixtures_table = self.browser.find_element(
                locator_type=LocatorType.CSS_SELECTOR,
                locator_value="#live-table > div.event.event--fixtures > div > div",
                suppress_exception=True,
            )

        if fixtures_table is None:
            print(
                "Critical Error: Unable to find fixtures table in the league page!!! Aborting..."
            )
            raise Exception("Unable to find fixtures table in the league page!!!")

        number_of_rounds_found = self.load_all_rounds(fixtures_table)
        number_rounds_to_process = min(number_of_rounds_found, self.config.rounds)
        print(f"Number of rounds to process: {number_rounds_to_process}")

        matches = extract_matches(fixtures_table, number_rounds_to_process)

        return matches
