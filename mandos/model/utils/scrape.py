from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

from pocketutils.core.query_utils import QueryExecutor

from mandos.model.settings import MANDOS_SETTINGS

from mandos.model.utils.setup import logger


try:
    import selenium
except ImportError:
    selenium = None
    logger.info("Selenium is not installed")


# noinspection PyBroadException
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
except Exception:
    webdriver = None
    WebDriver = None
    By = None

if webdriver is not None:
    # noinspection PyBroadException
    try:
        driver_fn = getattr(webdriver, MANDOS_SETTINGS.selenium_driver)
        logger.notice(f"Loaded Selenium driver {MANDOS_SETTINGS.selenium_driver}")
    except AttributeError:
        driver_fn = None
        logger.warning(f"Selenium driver {MANDOS_SETTINGS.selenium_driver} not found")


@dataclass(frozen=True)
class Scraper:
    driver: WebDriver
    executor: QueryExecutor

    @classmethod
    def create(cls, executor: QueryExecutor) -> Scraper:
        if driver_fn is None:
            raise ValueError(f"Selenium driver {MANDOS_SETTINGS.selenium_driver} not found")
        return Scraper(driver_fn(), executor)

    def go(self, url: str) -> Scraper:
        self.driver.get(url)
        # self.driver.find_elements_by_link_text("1")
        return self

    def find_element(self, thing: str, by: str) -> WebElement:
        by = by.upper()
        return self.driver.find_element(thing, by)

    def find_elements(self, thing: str, by: str) -> Sequence[WebElement]:
        by = by.upper()
        return self.driver.find_elements(thing, by)

    def click_element(self, thing: str, by: str) -> None:
        by = by.upper()
        element = self.driver.find_element(thing, by)
        element.click()


__all__ = ["Scraper", "By"]