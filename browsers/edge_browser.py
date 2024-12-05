from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from selenium.webdriver import Edge, EdgeOptions

from browsers.base_browser import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    BaseBrowser,
)
from logging_config import get_logger


class EdgeOptionArguments(Enum):
    """Edge browser options arguments."""

    HEADLESS = "--headless=new"
    NO_SANDBOX = "--no-sandbox"
    DISABLE_DEV_SHM = "--disable-dev-shm-usage"
    DISABLE_GPU = "--disable-gpu"
    DISABLE_EXTENSIONS = "--disable-extensions"
    DISABLE_NOTIFICATIONS = "--disable-notifications"
    DISABLE_INFOBARS = "--disable-infobars"
    START_MAXIMIZED = "--start-maximized"
    INPRIVATE = "--inprivate"
    WINDOW_SIZE = "--window-size"
    DISABLE_LOGGING = "--disable-logging"
    LOG_LEVEL = "--log-level"


class EdgeBrowser(BaseBrowser):
    def __init__(
        self,
        options_args: Optional[
            Union[List[EdgeOptionArguments], List[Tuple[EdgeOptionArguments, Any]]]
        ] = None,
    ) -> None:
        """
        Initialize Edge browser with specified options.

        Args:
            options_args: Optional list of EdgeOptionArguments or tuples of (EdgeOptionArguments, value)
                        For simple flags, use EdgeOptionArguments alone
                        For options requiring values (like window size), use (EdgeOptionArguments, value) tuple
        """
        self.logger = get_logger(__name__)
        edge_options = EdgeOptions()

        # Add logging control options
        edge_options.add_argument(EdgeOptionArguments.DISABLE_LOGGING.value)
        edge_options.add_argument(
            f"{EdgeOptionArguments.LOG_LEVEL.value}=3"
        )  # ERROR level only
        edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        if options_args:
            for arg in options_args:
                if isinstance(arg, tuple):
                    option, value = arg
                    if option == EdgeOptionArguments.WINDOW_SIZE:
                        edge_options.add_argument(
                            f"{option.value}={value[0]},{value[1]}"
                        )
                    else:
                        edge_options.add_argument(f"{option.value}={value}")
                else:
                    edge_options.add_argument(arg.value)
        else:
            # Set default window size if no options provided
            edge_options.add_argument(
                f"{EdgeOptionArguments.WINDOW_SIZE.value}={DEFAULT_WINDOW_WIDTH},{DEFAULT_WINDOW_HEIGHT}"
            )

        # Initialize Edge driver with options
        driver = Edge(options=edge_options)

        # Call parent class constructor
        super().__init__(driver=driver)

        self.logger.info("Edge browser initialized successfully.")
