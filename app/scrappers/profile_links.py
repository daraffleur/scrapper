from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.logger import log
from app.scrappers.scrapper import Scrapper
from app.scrappers import ProfileScrapper
from app.utils import LINKEDIN_BASE_URL
from links import links


class ProfileLinksScrapper(Scrapper):
    def scrape_or_check(self, search_keyword):
        # self.search_linkedin_profiles_by_keyword(search_keyword)
        """Get list of profiles` links"""
        # profile_links = self.get_profiles_links()
        self.maximize_window()
        # linkss = ["https://www.linkedin.com/in/dana-romaniuk/"]
        # for link in profile_links:
        for link in links:
            # for link in profile_links:
            """Check if profile has already scrapped"""
            if not self.db.profile_is_already_scrapped(link):
                """Scrape profile by link"""
                profile_scrapper = ProfileScrapper(self.db, self.driver)
                profile = profile_scrapper.scrape_or_check(link)
                personal_info = profile.personal_info
                """Parse personal Info"""
                name = personal_info["name"]
                headline = personal_info["headline"]
                company = personal_info["company"]
                school = personal_info["school"]
                location = personal_info["location"]
                summary = personal_info["summary"]
                image = personal_info["image"]
                email = personal_info["email"]
                phone = personal_info["phone"]
                connected = personal_info["connected"]
                birth = personal_info["birth"]
                address = personal_info["address"]
                twitter = personal_info["twitter"]
                profile_url = personal_info["profile_url"]
                websites = personal_info["websites"]
                data = (
                    link,
                    name,
                    headline,
                    company,
                    school,
                    location,
                    summary,
                    image,
                    email,
                    phone,
                    connected,
                    birth,
                    address,
                    twitter,
                    profile_url,
                    websites,
                )
                self.db.insert_profile(data)
                log(log.INFO, "New profile is added to DB")

                """Check if there is enough contact info """

                """Make contact with a profile"""
                self.find_element_by_class_name("artdeco-modal-overlay").click()
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
            self.scroll_page()
            # self.sleep()
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
                self.wait_for_element_ready(By.CSS_SELECTOR, ".entity-result__item a")

            except (TimeoutException) as error:
                log(log.INFO, "Last page reached", error)
                break
        return profile_links
