"""Browser utilities."""

from __future__ import annotations

import logging
import os
import threading
from typing import List

from fake_useragent import FakeUserAgentError, UserAgent
import undetected_chromedriver as uc

from ..utils.cookies import load_cookies_from_file, save_cookies_to_file


WITH_PROXIES = False

class Browser:
    __instance = None

    @staticmethod
    def get():
        # print("Browser.getBrowser() called")
        if Browser.__instance is None:
            with threading.Lock():
                if Browser.__instance is None:
                    # print("Creating new browser instance due to no instance found")
                    Browser.__instance = Browser()
        return Browser.__instance

    def __init__(self):
        if Browser.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Browser.__instance = self
        self.user_agent = ""
        options = uc.ChromeOptions()
        self._driver = uc.Chrome(options=options)
        self.with_random_user_agent()
        logging.debug("Браузер инициализирован")

    def with_random_user_agent(self, fallback: str | None = None) -> None:
        """Set random user agent.

        Args:
            fallback: Значение по умолчанию, если не удаётся получить случайный user-agent.
        """
        try:
            self.user_agent = UserAgent().random
        except FakeUserAgentError as e:
            if fallback:
                self.user_agent = fallback
            else:
                raise e
        logging.debug("User-Agent установлен: %s", self.user_agent)

    @property
    def driver(self):
        """Возвращает экземпляр webdriver."""
        return self._driver

    def load_cookies_from_file(self, filename: str) -> None:
        """Загружает cookies в браузер."""
        cookies = load_cookies_from_file(filename)
        for cookie in cookies:
            self._driver.add_cookie(cookie)
        self._driver.refresh()

    def save_cookies(self, filename: str, cookies: List[dict] | None = None) -> None:
        """Сохраняет cookies на диск."""
        save_cookies_to_file(cookies, filename)


if __name__ == "__main__":
    import os
    # get current relative path of this file.
    print(os.path.dirname(os.path.abspath(__file__)))
