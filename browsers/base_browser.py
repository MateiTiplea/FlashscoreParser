import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from settings import LOGGING_LEVEL, set_global_driver

logging.basicConfig(level=LOGGING_LEVEL)
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
DEFAULT_TIMEOUT = 10


class LocatorType(Enum):
    """Enumeration of supported locator types."""

    ID = By.ID
    NAME = By.NAME
    XPATH = By.XPATH
    CLASS_NAME = By.CLASS_NAME
    CSS_SELECTOR = By.CSS_SELECTOR
    LINK_TEXT = By.LINK_TEXT
    PARTIAL_LINK_TEXT = By.PARTIAL_LINK_TEXT
    TAG_NAME = By.TAG_NAME


class BaseBrowser:
    def __init__(self, driver: WebDriver) -> None:
        self.driver: WebDriver = driver
        set_global_driver(driver=self.driver)

    def open_url(self, url: str) -> None:
        self.driver.get(url=url)

    def quit(self) -> None:
        self.driver.quit()
        logging.info("Quit the driver and closed all associated windows.")

    def find_element(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        wait_for_visibility: bool = True,
        suppress_exception: bool = False,
    ) -> Optional[WebElement]:
        """
        Find a single element using the specified locator.

        Args:
            locator_type: Type of locator to use (can be LocatorType enum or string)
            locator_value: Value of the locator
            timeout: Maximum time to wait for element (seconds)
            wait_for_visibility: If True, wait for element to be visible, not just present

        Returns:
            WebElement if found, None otherwise

        Raises:
            TimeoutException: If element is not found within timeout period
        """
        try:
            # Convert string to LocatorType if necessary
            if isinstance(locator_type, str):
                locator_type = LocatorType[locator_type.upper()]

            # Create wait condition based on visibility flag
            condition = (
                EC.visibility_of_element_located
                if wait_for_visibility
                else EC.presence_of_element_located
            )

            element = WebDriverWait(self.driver, timeout).until(
                condition((locator_type.value, locator_value))
            )
            return element
        except TimeoutException:
            if not suppress_exception:
                logging.warning(
                    f"Element not found with {locator_type.name}='{locator_value}' "
                    f"after {timeout} seconds"
                )
            return None
        except Exception as e:
            if not suppress_exception:
                logging.error(
                    f"Error finding element with {locator_type.name}='{locator_value}': {str(e)}"
                )
            return None

    def find_elements(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        wait_for_visibility: bool = True,
        suppress_exception: bool = False,
    ) -> List[WebElement]:
        """
        Find all elements matching the specified locator.

        Args:
            locator_type: Type of locator to use (can be LocatorType enum or string)
            locator_value: Value of the locator
            timeout: Maximum time to wait for elements (seconds)
            wait_for_visibility: If True, wait for elements to be visible, not just present

        Returns:
            List of WebElements if found, empty list otherwise
        """
        try:
            # Convert string to LocatorType if necessary
            if isinstance(locator_type, str):
                locator_type = LocatorType[locator_type.upper()]

            # Create wait condition based on visibility flag
            condition = (
                EC.visibility_of_all_elements_located
                if wait_for_visibility
                else EC.presence_of_all_elements_located
            )

            elements = WebDriverWait(self.driver, timeout).until(
                condition((locator_type.value, locator_value))
            )
            return elements
        except TimeoutException:
            if not suppress_exception:
                logging.warning(
                    f"No elements found with {locator_type.name}='{locator_value}' "
                    f"after {timeout} seconds"
                )
            return []
        except Exception as e:
            if not suppress_exception:
                logging.error(
                    f"Error finding elements with {locator_type.name}='{locator_value}': {str(e)}"
                )
            return []

    def is_element_present(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Check if an element is present on the page.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            timeout: Maximum time to wait for element (seconds)

        Returns:
            bool: True if element is present, False otherwise
        """
        return (
            self.find_element(
                locator_type=locator_type,
                locator_value=locator_value,
                timeout=timeout,
                wait_for_visibility=False,
                suppress_exception=suppress_exception,
            )
            is not None
        )

    def wait_for_element_to_disappear(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Wait for an element to disappear from the page.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            timeout: Maximum time to wait for element disappearance (seconds)

        Returns:
            bool: True if element disappeared, False if timeout occurred
        """
        try:
            # Convert string to LocatorType if necessary
            if isinstance(locator_type, str):
                locator_type = LocatorType[locator_type.upper()]

            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((locator_type.value, locator_value))
            )
            return True
        except TimeoutException:
            if not suppress_exception:
                logging.warning(
                    f"Element with {locator_type.name}='{locator_value}' "
                    f"did not disappear after {timeout} seconds"
                )
            return False
        except Exception as e:
            if not suppress_exception:
                logging.error(
                    f"Error waiting for element disappearance with {locator_type.name}"
                    f"='{locator_value}': {str(e)}"
                )
            return False

    def get_element_text(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> Optional[str]:
        """
        Get text content of an element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            timeout: Maximum time to wait for element

        Returns:
            String content of element if found, None otherwise
        """
        element = self.find_element(
            locator_type, locator_value, timeout, suppress_exception
        )
        return element.text if element else None

    def get_element_attribute(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        attribute: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> Optional[str]:
        """
        Get specified attribute value of an element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            attribute: Name of the attribute to retrieve
            timeout: Maximum time to wait for element

        Returns:
            Attribute value if found, None otherwise
        """
        element = self.find_element(
            locator_type, locator_value, timeout, suppress_exception
        )
        return element.get_attribute(attribute) if element else None

    def click_element(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Click on an element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            timeout: Maximum time to wait for element

        Returns:
            True if click successful, False otherwise
        """
        try:
            element = self.find_element(
                locator_type, locator_value, timeout, suppress_exception
            )
            if element and element.is_enabled():
                element.click()
                return True
            return False
        except ElementNotInteractableException:
            logging.error(f"Element not interactable: {locator_type}='{locator_value}'")
            return False

    def input_text(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        text: str,
        clear_first: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Input text into an element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            text: Text to input
            clear_first: Whether to clear existing text first
            timeout: Maximum time to wait for element

        Returns:
            True if input successful, False otherwise
        """
        try:
            element = self.find_element(
                locator_type, locator_value, timeout, suppress_exception
            )
            if element and element.is_enabled():
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            return False
        except ElementNotInteractableException:
            logging.error(f"Element not interactable: {locator_type}='{locator_value}'")
            return False

    def select_dropdown_option(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        option_text: Optional[str] = None,
        option_value: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Select an option from a dropdown element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            option_text: Visible text of the option to select
            option_value: Value attribute of the option to select
            timeout: Maximum time to wait for element

        Returns:
            True if selection successful, False otherwise
        """
        try:
            element = self.find_element(
                locator_type, locator_value, timeout, suppress_exception
            )
            if element:
                select = Select(element)
                if option_text:
                    select.select_by_visible_text(option_text)
                elif option_value:
                    select.select_by_value(option_value)
                else:
                    logging.error("Either option_text or option_value must be provided")
                    return False
                return True
            return False
        except Exception as e:
            logging.error(f"Error selecting dropdown option: {str(e)}")
            return False

    def get_element_state(
        self,
        locator_type: Union[LocatorType, str],
        locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> Dict[str, bool]:
        """
        Get various states of an element.

        Args:
            locator_type: Type of locator to use
            locator_value: Value of the locator
            timeout: Maximum time to wait for element

        Returns:
            Dictionary containing element states (displayed, enabled, selected)
        """
        element = self.find_element(
            locator_type, locator_value, timeout, suppress_exception
        )
        if not element:
            return {"displayed": False, "enabled": False, "selected": False}

        return {
            "displayed": element.is_displayed(),
            "enabled": element.is_enabled(),
            "selected": element.is_selected(),
        }

    def get_table_data(
        self,
        table_locator_type: Union[LocatorType, str],
        table_locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> List[List[str]]:
        """
        Extract data from an HTML table.

        Args:
            table_locator_type: Type of locator for the table
            table_locator_value: Value of the table locator
            timeout: Maximum time to wait for element

        Returns:
            List of rows, where each row is a list of cell values
        """
        table = self.find_element(
            table_locator_type, table_locator_value, timeout, suppress_exception
        )
        if not table:
            return []

        rows = table.find_elements(
            By.TAG_NAME, "tr", timeout=timeout, suppress_exception=suppress_exception
        )
        table_data = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(
                By.TAG_NAME, "th"
            )
            row_data = [cell.text.strip() for cell in cells]
            if any(row_data):  # Only add non-empty rows
                table_data.append(row_data)

        return table_data

    # custom function for pressing a button after with ads on the page
    def handle_overlay_and_click(
        self,
        target_locator_type: Union[LocatorType, str],
        target_locator_value: str,
        timeout: int = DEFAULT_TIMEOUT,
        suppress_exception: bool = False,
    ) -> bool:
        """
        Handle any overlays and click the target element.

        Args:
            target_locator_type: Type of locator for target element
            target_locator_value: Value of the locator for target element
            timeout: Maximum time to wait

        Returns:
            bool: True if click was successful, False otherwise
        """
        try:
            # First try to find and handle the ad overlay
            ad_overlay = self.find_element(
                locator_type=LocatorType.CLASS_NAME,
                locator_value="adsclick",
                timeout=5,
                suppress_exception=suppress_exception,
            )

            if ad_overlay:
                # Try to remove the ad overlay using JavaScript
                self.driver.execute_script(
                    """
                    var elements = document.getElementsByClassName('adsclick');
                    for(var i=0; i<elements.length; i++){
                        elements[i].remove();
                    }
                """
                )

            # Now try to click the target element
            element = self.find_element(
                locator_type=target_locator_type,
                locator_value=target_locator_value,
                timeout=timeout,
                suppress_exception=suppress_exception,
            )

            if element:
                # Scroll element into view
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", element
                )
                # Add a small delay to allow any animations to complete
                import time

                time.sleep(0.5)
                # Try to click using JavaScript
                self.driver.execute_script("arguments[0].click();", element)
                return True

            return False

        except Exception as e:
            logging.error(f"Error handling overlay and clicking element: {str(e)}")
            return False
