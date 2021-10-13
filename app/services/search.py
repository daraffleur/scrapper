import time

from app.logger import log
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class SearchService:
    def __init__(self, driver, holdup: int, linkedin_base_url: str):
        self.driver = driver
        self.holdup = holdup
        self.linkedin_base_url = linkedin_base_url

    def search_linkedin_profiles(self, keyword):
        log(log.INFO, "Searching profiles page")
        self.driver.get("https://www.linkedin.com/search/results/people/")

        # search based on keywords
        self.wait_for_element_ready(By.CLASS_NAME, "search-global-typeahead__input")
        time.sleep(self.holdup)
        search_bars = self.driver.find_elements_by_class_name(
            "search-global-typeahead__input"
        )
        self.driver.maximize_window()

        search_keywords = search_bars[0]
        search_keywords.send_keys(keyword)
        search_keywords.send_keys(Keys.RETURN)
        log(log.INFO, "Profiles have searched successfully")
        time.sleep(self.holdup)

    def wait_for_element_ready(self, by, text: str):
        """Waits for an element to be ready

        Parameters
        ----------
        by : Selenium BY object
        """
        try:
            WebDriverWait(self.driver, self.holdup).until(
                EC.presence_of_element_located((by, text))
            )
        except TimeoutException:
            log(log.DEBUG, "wait_for_element_ready TimeoutException")
            pass

    def get_related_profiles_links(self):
        profile_links = []
        for page in range(2, 3):
            profiles = self.driver.find_elements_by_css_selector(
                ".entity-result__item a"
            )
            for profile in profiles:
                link = profile.get_attribute("href")
                profile_links.append(link)

        return profile_links
