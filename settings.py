from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from logging_config import setup_logging

setup_logging()
GLOBAL_DRIVER: Optional[WebDriver] = None


def set_global_driver(driver: WebDriver):
    global GLOBAL_DRIVER
    GLOBAL_DRIVER = driver
