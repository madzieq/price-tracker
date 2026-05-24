import logging
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from app.core.config import settings

logger = logging.getLogger(__name__)

PRICE_SELECTORS = {
    "allegro": [
        "[data-role='price-value']",
        ".price-primary",
        "span[aria-label*='cena']",
    ],
    "mediamarkt": [
        ".price__main-price",
        "[data-test='product-price']",
    ],
    "x-kom": [
        ".price-box",
        "[class*='ProductPrice']",
    ],
    "default": [
        "[class*='price']",
        "[itemprop='price']",
        "[data-price]",
    ],
}


class PriceScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def _get_driver(self) -> webdriver.Remote:
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        return webdriver.Remote(
            command_executor=settings.SELENIUM_HUB_URL,
            options=options,
        )

    def get_price(self, url: str) -> float | None:
        driver = self._get_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
            )
            shop = self._detect_shop(url)
            selectors = PRICE_SELECTORS.get(shop, PRICE_SELECTORS["default"])

            for selector in selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        expected_conditions.presence_of_element_located(
                            (By.CSS_SELECTOR, selector)
                        )
                    )
                    price_text = element.text or element.get_attribute("content") or ""
                    price = self._parse_price(price_text)
                    if price:
                        return price
                except (TimeoutException, NoSuchElementException):
                    continue

            logger.warning(f"No price found for {url}")
            return None
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return None
        finally:
            driver.quit()

    def _detect_shop(self, url: str) -> str:
        for shop in PRICE_SELECTORS:
            if shop in url:
                return shop
        return "default"

    def _parse_price(self, text: str) -> float | None:
        cleaned = re.sub(r"[^\d,\.]", "", text.replace("\xa0", ""))
        cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
