# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.scrappers.scrapper import Scrapper
from app.services import Profile
from app.logger import log
from app.utils import AnyEC


class ProfileScrapper(Scrapper):
    """Scraper for Personal LinkedIn Profiles."""

    MAIN_SELECTOR = ".scaffold-layout__main"
    ERROR_SELECTOR = ".profile-unavailable"

    def scrape(self, link, user=None):
        self.load_profile_page(link, user)
        return self.get_profile()

        # self.get_url(link)
        # self.sleep()

        # self.scroll_page()
        # html = self.driver.page_source
        # self.profile.get_soup(html)
        # """
        # Extracting the HTML of the complete introduction box
        # that contains the name, description, and the location
        # """
        # [name, description, location] = self.profile.get_introduction()

        # time.sleep(self.holdup)

        # self.scrapper.scroll_to_top()
        # self.get_contact_window()
        # content = self.driver.find_element_by_css_selector(
        #     ".pv-profile-section.pv-contact-info.artdeco-container-card.ember-view"
        # )
        # [email, birth_day] = self.profile.get_contact_info(content)

        # return [name, description, location, email, birth_day]

    # def get_contact_window(self):
    #     try:
    #         text = "Контактная информация"
    #         button = self.driver.find_element_by_partial_link_text(text)
    #         button.click()
    #         time.sleep(self.holdup)
    #     except Exception as error:
    #         log(
    #             log.WARNING,
    #             "Failed to open/get contact info HTML. Returning an empty string.",
    #             error,
    #         )
    #         return ""

    def load_profile_page(self, url="", user=None):
        """Load profile page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = "https://www.linkedin.com/in/" + user
        if "com/in/" not in url:
            raise ValueError("Url must look like... .com/in/NAME")

        log(log.DEBUG, "Start scraping profile for URL %s", url)

        self.get_url(url)

        """Wait for page to load dynamically via javascript"""
        try:
            WebDriverWait(self.driver, self.holdup).until(
                AnyEC(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.MAIN_SELECTOR)
                    ),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.ERROR_SELECTOR)
                    ),
                )
            )
        except TimeoutException as error:
            raise ValueError("Took too long to load profile: %s ", error)

        """Check if we got the 'profile unavailable' page"""
        try:
            self.find_element_by_css_selector(self.MAIN_SELECTOR)
        except Exception as error:
            raise ValueError(
                "Profile Unavailable: Profile link does not match any current Linkedin Profiles",
                error,
            )
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()
        self.expand_given_recommendations()

    def expand_given_recommendations(self):
        try:
            given_recommendation_tab = self.find_element_by_css_selector(
                'section.pv-recommendations-section button[aria-selected="false"].artdeco-tab'
            )
            """Scrolls the desired element into view"""
            self.driver.execute_script(
                "arguments[0].scrollIntoView(false);", given_recommendation_tab
            )
            given_recommendation_tab.click()
            self.click_expandable_buttons()
            # self.scroll_to_bottom()
        except Exception as error:
            log(
                log.EXCEPTION,
                "Exeption occured during expanding reccomendtions: %s",
                error,
            )
            pass

    def get_profile(self):
        try:
            profile = self.find_element_by_css_selector(
                self.MAIN_SELECTOR
            ).get_attribute("outerHTML")
        except Exception as exception:
            log(
                log.EXCEPTION,
                "Could not find profile wrapper html. This sometimes happens for exceptionally long profiles.  Try decreasing scroll-increment. The actual error was: %s",
                exception,
            )
            raise exception
        contact_info = self.get_contact_info()
        return Profile(profile + contact_info)

    def get_contact_info(self):
        try:
            # Scroll to top to put clickable button in view
            self.driver.execute_script("window.scrollTo(0, 0);")
            text = "Контактная информация"
            button = self.driver.find_element_by_partial_link_text(text)
            button.click()
            contact_info = self.wait_for_element_ready(By.CLASS_NAME, "pv-contact-info")
            return contact_info.get_attribute("outerHTML")
        except Exception as e:
            log(
                log.WARNING,
                "Failed to open/get contact info HTML. Returning an empty string.",
                e,
            )
            return ""


#     def get_mutual_connections(self):
#         try:
#             link = self.driver.find_element_by_partial_link_text("Mutual Connection")
#         except NoSuchElementException as e:
#             logger.warning(
#                 "Could not find a mutual connections link. Returning an empty list."
#             )
#             return []
#         with ConnectionScraper(scraperInstance=self) as cs:
#             cs.driver.get(link.get_attribute("href"))
#             cs.wait_for_el(".search-s-facet--facetNetwork form button")
#             return cs.scrape_all_pages()
