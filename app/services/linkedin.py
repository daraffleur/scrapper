import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.logger import log


class LinkedInService:
    def __init__(self, driver):
        """holdup: int, optional
        wait such amount of time and then do the following actions
        (thus LinkedIn does not run captcha)
        """
        self.driver = driver
        self.holdup = 6

    def wait_for_element_ready(self, by, text):
        """Waits for an element to be ready

        Parameters
        ----------
        by : Selenium BY object
        text : str
        """

        try:
            WebDriverWait(self.driver, self.holdup).until(
                EC.presence_of_element_located((by, text))
            )
        except TimeoutException:
            log(log.DEBUG, "wait_for_element_ready TimeoutException")
            pass

    def login(self, username: str, password: str):
        log(log.INFO, "Logging to LinkedIn")
        self.driver.maximize_window()
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(self.holdup)
        self.driver.find_element_by_id("username").send_keys(username)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password").send_keys(Keys.RETURN)
        time.sleep(self.holdup)

    def search_job(self, keyword: str, location: str):
        """Enter keywords into search bar"""
        log(log.INFO, "Searching page")
        self.driver.get("https://www.linkedin.com/jobs/")

        # search based on keywords and location and hit enter
        self.wait_for_element_ready(By.CLASS_NAME, "jobs-search-box__text-input")
        time.sleep(self.holdup)
        search_bars = self.driver.find_elements_by_class_name(
            "jobs-search-box__text-input"
        )
        self.driver.maximize_window()
        search_keywords = search_bars[0]
        search_keywords.send_keys(keyword)
        # search_location = search_bars[3]
        # print("Element is visible? " + str(search_location.is_displayed()))
        # search_location.send_keys(location)
        # time.sleep(self.holdup)
        # search_location.send_keys(Keys.RETURN)
        search_keywords.send_keys(Keys.RETURN)
        log(log.INFO, "Keyword search has been done successfully")
        time.sleep(self.holdup)
