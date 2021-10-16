import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Scrapper:
    def __init__(self, driver, holdup: int, linkedin_base_url: str):
        self.driver = driver
        self.holdup = holdup
        self.linkedin_base_url = linkedin_base_url

    def wait(self, condition):
        return WebDriverWait(self.driver, self.holdup).until(condition)

    def wait_for_el(self, selector):
        return self.wait(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def get_link(self, link):
        return self.driver.get(link)

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self):
        """Get scroll height"""
        last_scroll_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

        for i in range(3):
            """Scroll down to the bottom"""
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            """Wait to load page"""
            time.sleep(self.holdup)

            """Calculate new scroll height and compare with the last scroll height"""
            new_scroll_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            if new_scroll_height == last_scroll_height:
                break
            last_scroll_height = new_scroll_height
