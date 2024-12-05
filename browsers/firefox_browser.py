from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from selenium.webdriver import Firefox, FirefoxOptions

from browsers.base_browser import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    BaseBrowser,
)
from logging_config import get_logger


class FirefoxOptionArguments(Enum):
    """Firefox browser options arguments."""

    HEADLESS = "-headless"
    NO_SANDBOX = "--no-sandbox"
    DISABLE_GPU = "--disable-gpu"
    DISABLE_EXTENSIONS = "--disable-extensions"
    DISABLE_NOTIFICATIONS = "--disable-notifications"
    START_MAXIMIZED = "--start-maximized"
    PRIVATE = "-private-window"
    WINDOW_SIZE = "--window-size"
    DISABLE_LOGGING = "--disable-logging"
    LOG_LEVEL = "--log-level"


class FirefoxBrowser(BaseBrowser):
    def __init__(
        self,
        options_args: Optional[
            Union[
                List[FirefoxOptionArguments], List[Tuple[FirefoxOptionArguments, Any]]
            ]
        ] = None,
    ) -> None:
        """
        Initialize Firefox browser with specified options.

        Args:
            options_args: Optional list of FirefoxOptionArguments or tuples of (FirefoxOptionArguments, value)
                        For simple flags, use FirefoxOptionArguments alone
                        For options requiring values (like window size), use (FirefoxOptionArguments, value) tuple
        """
        self.logger = get_logger(__name__)

        firefox_options = FirefoxOptions()

        # Add logging control options - Firefox uses slightly different logging mechanism
        firefox_options.set_preference("browser.dom.window.dump.enabled", False)
        firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)
        firefox_options.set_preference("javascript.options.showInConsole", False)
        firefox_options.set_preference("browser.tabs.remote.autostart.2", False)

        # Set log level through capabilities
        firefox_options.log.level = "FATAL"  # Most restrictive log level

        if options_args:
            for arg in options_args:
                if isinstance(arg, tuple):
                    option, value = arg
                    if option == FirefoxOptionArguments.WINDOW_SIZE:
                        firefox_options.add_argument(
                            f"{option.value}={value[0]},{value[1]}"
                        )
                    else:
                        firefox_options.add_argument(f"{option.value}={value}")
                else:
                    firefox_options.add_argument(arg.value)
        else:
            # Set default window size if no options provided
            firefox_options.add_argument(
                f"{FirefoxOptionArguments.WINDOW_SIZE.value}={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}"
            )

        # Initialize Firefox driver with options
        driver = Firefox(options=firefox_options)

        # Call parent class constructor
        super().__init__(driver=driver)

        self.logger.info("Firefox browser initialized successfully.")
