import os
import sys
from pathlib import Path


class BrowserDetector:
    def __init__(self) -> None:
        self.detected_browsers = {}
        self._detect_browsers()

    def _detect_browsers(self) -> None:
        """Detect installed browsers based on the operating system."""
        if sys.platform == "win32":
            self._detect_windows_browsers()
        elif sys.platform == "darwin":
            self._detect_mac_browsers()
        else:  # Linux and other Unix-like systems
            self._detect_linux_browsers()

    def _detect_windows_browsers(self) -> None:
        """Detect browsers on Windows."""
        # Common installation paths on Windows
        paths = {
            "Chrome": [
                Path(
                    os.environ.get("PROGRAMFILES", ""),
                    "Google/Chrome/Application/chrome.exe",
                ),
                Path(
                    os.environ.get("PROGRAMFILES(X86)", ""),
                    "Google/Chrome/Application/chrome.exe",
                ),
            ],
            "Firefox": [
                Path(os.environ.get("PROGRAMFILES", ""), "Mozilla Firefox/firefox.exe"),
                Path(
                    os.environ.get("PROGRAMFILES(X86)", ""),
                    "Mozilla Firefox/firefox.exe",
                ),
            ],
            "Edge": [
                Path(
                    os.environ.get("PROGRAMFILES(X86)", ""),
                    "Microsoft/Edge/Application/msedge.exe",
                ),
                Path(
                    os.environ.get("PROGRAMFILES", ""),
                    "Microsoft/Edge/Application/msedge.exe",
                ),
            ],
        }

        for browser, browser_paths in paths.items():
            for path in browser_paths:
                if path.exists():
                    self.detected_browsers[browser] = str(path)
                    break

    def _detect_mac_browsers(self) -> None:
        """Detect browsers on macOS."""
        paths = {
            "Chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            "Firefox": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            "Edge": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
        }

        for browser, browser_paths in paths.items():
            for path in browser_paths:
                if Path(path).exists():
                    self.detected_browsers[browser] = path
                    break

    def _detect_linux_browsers(self) -> None:
        """Detect browsers on Linux."""
        # Common binary names in PATH
        browsers = {
            "Chrome": ["google-chrome", "google-chrome-stable"],
            "Firefox": ["firefox"],
            "Edge": ["microsoft-edge"],
        }

        for browser, commands in browsers.items():
            for cmd in commands:
                # Check if browser is in PATH
                if any(
                    Path(path) / cmd
                    for path in os.environ.get("PATH", "").split(os.pathsep)
                    if (Path(path) / cmd).exists()
                ):
                    self.detected_browsers[browser] = cmd
                    break

    def get_installed_browsers(self) -> list[str]:
        """Return a list of installed browsers."""
        return list(self.detected_browsers.keys())

    def select_browser(self) -> dict[str, str]:
        """Interactive prompt for user to select a browser."""
        if not self.detected_browsers:
            print("No supported browsers detected on your system.")
            return None

        print("\nDetected browsers:")
        for idx, browser in enumerate(self.detected_browsers.keys(), 1):
            print(f"{idx}. {browser}")

        while True:
            try:
                choice = input("\nSelect a browser (enter the number): ")
                index = int(choice) - 1
                browsers = list(self.detected_browsers.keys())

                if 0 <= index < len(browsers):
                    selected_browser = browsers[index]
                    return {
                        "name": selected_browser,
                        "path": self.detected_browsers[selected_browser],
                    }
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
