import os
import pickle

from app.logger import log
from app.utils import PATH_TO_COOKIES


class CookiesService:
    def __init__(self, driver):
        self.driver = driver

    def check_cookies(self):
        return True if os.path.exists(PATH_TO_COOKIES) else False

    def load_cookies(self):
        with open(PATH_TO_COOKIES, "rb") as cookies_file:
            cookies = pickle.load(cookies_file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def save_cookies(self):
        """Saves browser cookies"""

        with open(PATH_TO_COOKIES, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)
            log(log.INFO, "Cookies have been saved to %s", PATH_TO_COOKIES)
