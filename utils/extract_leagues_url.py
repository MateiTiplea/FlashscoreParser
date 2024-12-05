import json
import logging
import os
import sys
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By

from browsers.base_browser import BaseBrowser, LocatorType
from browsers.browser_factory import BrowserFactory, BrowserType
from browsers.edge_browser import EdgeOptionArguments
from settings import LOGGING_LEVEL

logging.basicConfig(level=LOGGING_LEVEL)


def get_countries_urls() -> dict[str, str]:
    data = None
    with open(
        os.path.join(os.path.dirname(__file__), "locations_url_mapping.json"),
        "r",
        encoding="utf-8",
    ) as fin:
        data = json.load(fin)
    return data


def dump_result(data: dict) -> None:
    with open(
        os.path.join(os.path.dirname(__file__), "leagues_url_mapping.json"),
        "w",
        encoding="utf-8",
    ) as fout:
        json.dump(data, fout, indent=4)


def get_leagues_from_country(browser: BaseBrowser, country_url: str) -> dict[str, str]:
    browser.open_url(country_url)

    # remove the accept cookies from the page
    possible_cookie_selector = "#onetrust-accept-btn-handler"
    if browser.is_element_present(
        locator_type=LocatorType.CSS_SELECTOR,
        locator_value=possible_cookie_selector,
        timeout=2,  # Short timeout since we're trying multiple selectors
        # suppress_exception=True,
    ):
        cookie_button = browser.find_element(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value=possible_cookie_selector,
            timeout=2,  # Short timeout since we're trying multiple selectors
            # suppress_exception=True,
        )
        if cookie_button:
            browser.click_element(
                locator_type=LocatorType.CSS_SELECTOR,
                locator_value=possible_cookie_selector,
                # suppress_exception=True,
            )
            # Wait for banner to disappear
            browser.wait_for_element_to_disappear(
                locator_type=LocatorType.ID,
                locator_value="#onetrust-banner-sdk",
                # suppress_exception=True,
            )

    leagues = dict()
    # Check if leagues zone exists
    leagues_zone = browser.find_element(
        locator_type=LocatorType.CSS_SELECTOR,
        locator_value="div.selected-country-list",
        timeout=10,  # Increased timeout for main content
    )

    if not leagues_zone:
        logging.warning(f"Could not find leagues zone for country url {country_url}")
        return leagues

    if browser.is_element_present(
        locator_type=LocatorType.CSS_SELECTOR,
        locator_value="div.selected-country-list div.show-more",
        timeout=1,
        # suppress_exception=True,
    ):
        clicked = browser.click_element(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value="div.selected-country-list div.show-more",
            timeout=1,
        )
        if clicked:
            print("Clicked show more success")
        else:
            print("Failed to click show more")

    # Get all league blocks
    try:
        blocks = leagues_zone.find_elements(By.CSS_SELECTOR, "div.leftMenu__item")
        logging.info(f"Found {len(blocks)} league blocks for country url {country_url}")
    except (NoSuchElementException, StaleElementReferenceException) as e:
        logging.warning(
            f"Error finding league blocks for country url {country_url}: {str(e)}"
        )
        return leagues

    # Process each block
    for block in blocks:
        try:
            # Get block text first
            block_text = block.text.strip()
            if not block_text:
                continue

            # Try to find anchor tag
            try:
                anchor = block.find_element(By.TAG_NAME, "a")
                if not anchor:
                    logging.debug(
                        f"No anchor tag found for block '{block_text}' in {country_url}"
                    )
                    continue

                # Get the first valid anchor with href
                href = anchor.get_attribute("href")
                if href:
                    leagues[block_text] = href
                    continue

            except NoSuchElementException:
                logging.debug(
                    f"No anchor tag found for block '{block_text}' in {country_url}"
                )
                continue

        except StaleElementReferenceException:
            logging.warning(
                f"Stale element encountered while processing block in {country_url}"
            )
            continue
        except Exception as e:
            logging.warning(
                f"Unexpected error processing block in {country_url}: {str(e)}"
            )
            continue

    logging.info(f"Successfully extracted {len(leagues)} leagues from {country_url}")
    return leagues


def main():
    browser = BrowserFactory().create_browser(
        browser_type=BrowserType.EDGE,
        # options_args=[EdgeOptionArguments.HEADLESS]
    )

    countries = get_countries_urls()
    leagues_mapping = dict()
    for country, country_url in countries.items():
        leagues_mapping[country] = get_leagues_from_country(browser, country_url)

    browser.quit()

    dump_result(leagues_mapping)


if __name__ == "__main__":
    main()
