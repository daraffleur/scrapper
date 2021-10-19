from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.logger import log
from app.scrappers.scrapper import Scrapper
from app.utils import LINKEDIN_BASE_URL


class ProfileLinksScrapper(Scrapper):
    def scrape(self, search_keyword):
        self.search_linkedin_profiles_by_keyword(search_keyword)
        """Get list of profiles` links"""
        # profile_links = self.get_profiles_links()
        profile_links = [
            "https://www.linkedin.com/in/dana-romaniuk/",
            "https://www.linkedin.com/in/vkhmura/",
        ]
        for link in profile_links:
            """Check if link has already been in db; if not - insert link to db"""
            if not self.db.profile_link_is_in_db(link):
                self.db.insert_profile_link(link)
        self.sleep()
        log(log.INFO, "Done scrapping profile links")

    def search_linkedin_profiles_by_keyword(self, keyword):
        log(log.INFO, "Searching profiles page")
        self.get_url(f"{LINKEDIN_BASE_URL}/search/results/people/")
        self.wait_for_element_ready(By.CLASS_NAME, "search-global-typeahead__input")
        self.sleep()

        # search based on keywords
        search_bars = self.find_elements_by_class_name("search-global-typeahead__input")
        self.maximize_window()
        search_keywords = search_bars[0]
        search_keywords.send_keys(keyword)
        search_keywords.send_keys(Keys.RETURN)
        log(log.INFO, "Profiles have searched successfully")
        self.sleep()

    def get_profiles_links(self):
        profile_links = []
        while True:
            profiles = self.find_elements_by_css_selector(".entity-result__item a")
            for profile in profiles:
                link = profile.get_attribute("href")
                if "search/results/people/" not in link and link not in profile_links:
                    profile_links.append(link)
                    # self.short_sleep()
            self.scroll_to_bottom()
            self.sleep()
            try:
                next_page_button_class = "artdeco-pagination__button--next"
                self.driver.execute_script(
                    "return arguments[0].scrollIntoView(true);",
                    WebDriverWait(self.driver, self.holdup).until(
                        EC.element_to_be_clickable(
                            (By.CLASS_NAME, next_page_button_class)
                        )
                    ),
                )
                next_page_button = self.find_element_by_class_name(
                    next_page_button_class
                )
                next_page_button.click()
                log(log.INFO, "Navigating to the next page")

            except (TimeoutException) as error:
                log(log.INFO, "Last page reached", error)
                break
        return profile_links
