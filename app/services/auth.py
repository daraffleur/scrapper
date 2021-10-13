import time

from selenium.webdriver.common.keys import Keys

from app.logger import log


class AuthService:
    def __init__(self, driver, holdup: int, linkedin_base_url: str):
        self.driver = driver
        self.holdup = holdup
        self.linkedin_base_url = linkedin_base_url

    def login_to_linkedin(self, username: str, password: str):

        log(log.INFO, "Logging to LinkedIn")
        self.driver.maximize_window()
        self.driver.get(f"{self.linkedin_base_url}/login")

        time.sleep(self.holdup)

        self.driver.find_element_by_id("username").send_keys(username)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password").send_keys(Keys.RETURN)

        time.sleep(self.holdup)

        log(log.INFO, "Logged in to LinkedIn")
