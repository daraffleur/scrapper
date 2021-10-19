import time

from selenium.webdriver.common.keys import Keys

from app.logger import log
from app.utils import LINKEDIN_BASE_URL


class AuthService:
    def __init__(self, driver):
        self.holdup = 6
        self.driver = driver

    def login_to_linkedin(self, username: str, password: str):

        log(log.INFO, "Logging to LinkedIn")
        self.driver.maximize_window()
        self.driver.get(f"{LINKEDIN_BASE_URL}/login")

        time.sleep(self.holdup)

        self.driver.find_element_by_id("username").send_keys(username)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password").send_keys(Keys.RETURN)

        time.sleep(self.holdup)

        log(log.INFO, "Logged in to LinkedIn")
