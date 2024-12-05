from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from selenium.webdriver import Chrome, ChromeOptions

from browsers.base_browser import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    BaseBrowser,
)
from logging_config import get_logger


class ChromeOptionArguments(Enum):
    """Chrome browser options arguments."""

    HEADLESS = "--headless=new"
    NO_SANDBOX = "--no-sandbox"
    DISABLE_DEV_SHM = "--disable-dev-shm-usage"
    DISABLE_GPU = "--disable-gpu"
    DISABLE_EXTENSIONS = "--disable-extensions"
    DISABLE_NOTIFICATIONS = "--disable-notifications"
    DISABLE_INFOBARS = "--disable-infobars"
    START_MAXIMIZED = "--start-maximized"
    INCOGNITO = "--incognito"
    WINDOW_SIZE = "--window-size"
    DISABLE_LOGGING = "--disable-logging"
    LOG_LEVEL = "--log-level"


class ChromeBrowser(BaseBrowser):
    def __init__(
        self,
        options_args: Optional[
            Union[List[ChromeOptionArguments], List[Tuple[ChromeOptionArguments, Any]]]
        ] = None,
    ) -> None:
        """
        Initialize Chrome browser with specified options.

        Args:
            options_args: Optional list of ChromeOptionArguments or tuples of (ChromeOptionArguments, value)
                        For simple flags, use ChromeOptionArguments alone
                        For options requiring values (like window size), use (ChromeOptionArguments, value) tuple
        """
        self.logger = get_logger(__name__)
        chrome_options = ChromeOptions()

        # Add logging control options
        chrome_options.add_argument(ChromeOptionArguments.DISABLE_LOGGING.value)
        chrome_options.add_argument(
            f"{ChromeOptionArguments.LOG_LEVEL.value}=3"
        )  # ERROR level only
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        if options_args:
            for arg in options_args:
                if isinstance(arg, tuple):
                    option, value = arg
                    if option == ChromeOptionArguments.WINDOW_SIZE:
                        chrome_options.add_argument(
                            f"{option.value}={value[0]},{value[1]}"
                        )
                    else:
                        chrome_options.add_argument(f"{option.value}={value}")
                else:
                    chrome_options.add_argument(arg.value)
        else:
            # Set default window size if no options provided
            chrome_options.add_argument(
                f"{ChromeOptionArguments.WINDOW_SIZE.value}={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}"
            )

        # Initialize Chrome driver with options
        driver = Chrome(options=chrome_options)

        # Call parent class constructor
        super().__init__(driver=driver)

        self.logger.info("Chrome browser initialized successfully.")
