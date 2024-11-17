from enum import Enum, auto
from typing import Any, List, Optional, Tuple, Union

from browsers.base_browser import BaseBrowser
from browsers.browser_detector import BrowserDetector
from browsers.chrome_browser import ChromeBrowser, ChromeOptionArguments
from browsers.edge_browser import EdgeBrowser, EdgeOptionArguments
from browsers.firefox_browser import FirefoxBrowser, FirefoxOptionArguments


class BrowserType(Enum):
    """Enumeration of supported browser types."""

    CHROME = auto()
    FIREFOX = auto()
    EDGE = auto()

    @classmethod
    def from_string(cls, browser_name: str) -> "BrowserType":
        """Convert browser name string to BrowserType enum."""
        browser_map = {"Chrome": cls.CHROME, "Firefox": cls.FIREFOX, "Edge": cls.EDGE}
        if browser_name not in browser_map:
            raise ValueError(f"Unsupported browser: {browser_name}")
        return browser_map[browser_name]


class BrowserFactory:
    """Factory class for creating browser instances."""

    def __init__(self):
        self.browser_detector = BrowserDetector()

    def get_available_browsers(self) -> List[BrowserType]:
        """Get list of available browsers on the system."""
        detected = self.browser_detector.get_installed_browsers()
        return [BrowserType.from_string(browser) for browser in detected]

    def create_browser(
        self,
        browser_type: Optional[BrowserType] = None,
        options_args: Optional[
            Union[
                List[ChromeOptionArguments],
                List[FirefoxOptionArguments],
                List[EdgeOptionArguments],
                List[
                    Tuple[
                        Union[
                            ChromeOptionArguments,
                            FirefoxOptionArguments,
                            EdgeOptionArguments,
                        ],
                        Any,
                    ]
                ],
            ]
        ] = None,
    ) -> BaseBrowser:
        """
        Create and return a browser instance of the specified type.

        Args:
            browser_type: Optional BrowserType enum value. If None, user will be prompted to select
            options_args: Optional browser-specific options arguments

        Returns:
            BaseBrowser: Instance of the specified browser

        Raises:
            ValueError: If specified browser is not available or no browsers are detected
        """
        if browser_type is None:
            # Let user select browser interactively
            selected = self.browser_detector.select_browser()
            if not selected:
                raise ValueError("No browsers detected on the system")
            browser_type = BrowserType.from_string(selected["name"])

        # Verify browser is available
        available_browsers = self.get_available_browsers()
        if browser_type not in available_browsers:
            raise ValueError(
                f"Browser {browser_type.name} is not available on this system"
            )

        # Create appropriate browser instance
        if browser_type == BrowserType.CHROME:
            return ChromeBrowser(options_args)
        elif browser_type == BrowserType.FIREFOX:
            return FirefoxBrowser(options_args)
        elif browser_type == BrowserType.EDGE:
            return EdgeBrowser(options_args)
