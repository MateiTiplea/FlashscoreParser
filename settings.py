from logging import INFO
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

LOGGING_LEVEL = INFO
GLOBAL_DRIVER: Optional[WebDriver] = None


def set_global_driver(driver: WebDriver):
    global GLOBAL_DRIVER
    GLOBAL_DRIVER = driver
