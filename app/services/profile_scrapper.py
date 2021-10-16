import time

from app.services.scrapper import Scrapper
from app.services.profile import Profile

from app.logger import log


class ProfileScraper:
    """Scraper for Personal LinkedIn Profiles."""

    def __init__(self, driver, holdup: int, linkedin_base_url: str):
        self.driver = driver
        self.holdup = holdup
        self.linkedin_base_url = linkedin_base_url
        self.profile = Profile()
        self.scrapper = Scrapper(driver, holdup, linkedin_base_url)

    def scrape(self, link):
        self.scrapper.get_link(link)
        time.sleep(self.holdup)

        self.scrapper.scroll_to_bottom()
        html = self.driver.page_source
        self.profile.get_soup(html)
        """
        Extracting the HTML of the complete introduction box
        that contains the name, description, and the location
        """
        [name, description, location] = self.profile.get_introduction()

        time.sleep(self.holdup)

        self.scrapper.scroll_to_top()
        self.get_contact_window()
        content = self.driver.find_element_by_css_selector(
            ".pv-profile-section.pv-contact-info.artdeco-container-card.ember-view"
        )
        [email, birth_day] = self.profile.get_contact_info(content)

        return [name, description, location, email, birth_day]

    def get_contact_window(self):
        try:
            text = "Контактная информация"
            button = self.driver.find_element_by_partial_link_text(text)
            button.click()
            time.sleep(self.holdup)
        except Exception as error:
            log(
                log.WARNING,
                "Failed to open/get contact info HTML. Returning an empty string.",
                error,
            )
            return ""
