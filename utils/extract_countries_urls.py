import json
import logging
import os
import sys

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


def get_menu_links(browser: BaseBrowser) -> dict[str, str]:
    """
    Get all menu links from lmc__block elements inside lmc__menu.

    Returns:
        Dictionary with text as key and href as value
    """
    menu_links = {}

    # Find all lmc__block elements within lmc__menu
    blocks = browser.find_elements(
        locator_type=LocatorType.CSS_SELECTOR,
        locator_value="div.lmc__menu div.lmc__block",
    )

    for block in blocks:
        try:
            # Get the text content of the block
            block_text = block.text.strip()

            # Find the anchor element within this block
            anchor = block.find_element(By.TAG_NAME, "a")

            # Get the href attribute
            href = anchor.get_attribute("href")

            # Add to dictionary if both text and href exist
            if block_text and href:
                menu_links[block_text] = href

        except (NoSuchElementException, StaleElementReferenceException) as e:
            logging.warning(f"Error processing menu block: {str(e)}")
            continue

    return menu_links


def main():
    factory = BrowserFactory()

    # available = factory.get_available_browsers()
    # print(f"Available browsers: {[b.name for b in available]}")

    browser = factory.create_browser(
        browser_type=BrowserType.EDGE, options_args=[EdgeOptionArguments.HEADLESS]
    )

    browser.open_url("https://www.flashscore.com/football/")

    possible_selectors = [
        "#onetrust-accept-btn-handler",
        ".accept-cookies-button",
        "[aria-label='Accept cookies']",
        "#onetrust-consent-sdk .accept-consent-button",
        ".cookie-accept",
        "#accept-cookies",
        "button[contains(text(), 'Accept')]",
    ]

    # Try each selector until we find the button
    for selector in possible_selectors:
        cookie_button = browser.find_element(
            locator_type=LocatorType.CSS_SELECTOR,
            locator_value=selector,
            timeout=2,  # Short timeout since we're trying multiple selectors
        )
        if cookie_button:
            browser.click_element(
                locator_type=LocatorType.CSS_SELECTOR, locator_value=selector
            )
            # Wait for banner to disappear
            browser.wait_for_element_to_disappear(
                locator_type=LocatorType.ID, locator_value="onetrust-banner-sdk"
            )
            break

    # After handling cookie banner, proceed with clicking the show more button
    clicked = browser.handle_overlay_and_click(
        target_locator_type=LocatorType.CSS_SELECTOR,
        target_locator_value="div.lmc__menu span.lmc__itemMore",
    )
    if clicked:
        print("Clicked show more success")
    else:
        print("Failed to click show more")

    locations_mapping = get_menu_links(browser)
    with open(
        os.path.join(os.path.dirname(__file__), "locations_url_mapping.json"),
        "w",
        encoding="utf-8",
    ) as fout:
        json.dump(locations_mapping, fout, indent=4)

    browser.quit()


if __name__ == "__main__":
    main()
