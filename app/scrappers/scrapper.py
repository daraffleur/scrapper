import os
import time

from abc import abstractmethod
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.logger import log
from app.database import Database
from app.utils import STORE_FOLDER_NAME


class Scrapper:
    """
    Wrapper for selenium driver with methods to scroll through a page and
    to scrape and parse info from a linkedin page

    Params:
        - db: instance of Database class (with opened connection and cursor)
        - driver {webdriver}: driver to be used for scraping
        - scroll_pause {float}: amount of time to pause (s) while incrementally
        scrolling through the page
        - scroll_increment {int}: pixel increment for scrolling
        - holdup {int}: time to wait for page to load (thus LinkedIn does not run captcha)
    """

    def __init__(
        self,
        db,
        driver,
        driver_options={},
        scroll_pause=0.1,
        scroll_increment=300,
        holdup=3,
    ):
        """holdup: int, optional
        wait such amount of time and then do the action
        (thus LinkedIn does not run captcha)
        """
        if type(self) is Scrapper:
            raise Exception(
                "Scraper is an abstract class and cannot be instantiated directly"
            )
        self.holdup = holdup
        self.was_passed_instance = False
        # self.driver = driver(**driver_options)
        self.driver = driver
        self.scroll_pause = scroll_pause
        self.scroll_increment = scroll_increment
        self.db = db

        self.setup_data_store()
        self.initialize_db()

    @abstractmethod
    def scrape_or_check(self):
        raise Exception("Must override abstract method scrape_or_check")

    def initialize_db(self):
        self.db = Database()
        self.db.create_linked_in_profiles_table()
        self.db.create_linked_in_contacts_table()

    def get_url(self, url):
        self.driver.get(url)

    def find_elements_by_class_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)

    def find_element_by_class_name(self, class_name):
        return self.driver.find_element_by_class_name(class_name)

    def find_elements_by_css_selector(self, selector):
        return self.driver.find_elements_by_css_selector(selector)

    def find_element_by_css_selector(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def find_element_by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)

    def get_html(self, url):
        self.load_profile_page(url)
        return self.driver.page_source

    def maximize_window(self):
        self.driver.maximize_window()

    def setup_data_store(self):
        """Create folder for saving files with data"""
        if not os.path.exists(STORE_FOLDER_NAME):
            os.makedirs(STORE_FOLDER_NAME)
            log(log.INFO, "%s folder is successfully created", STORE_FOLDER_NAME)

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page

        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        # NOTE: this starts scrolling from the current scroll position, not the top of the page.
        current_height = self.driver.execute_script(
            "return document.documentElement.scrollTop"
        )
        while True:
            # self.click_expandable_buttons()
            # Scroll down to bottom in increments of self.scroll_increment
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(
                    current_height + self.scroll_increment
                )
            )
            if new_height == current_height:
                break
            self.driver.execute_script("window.scrollTo(0, {});".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def scroll_page(self):
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

    def click_expandable_buttons(self):
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[aria-expanded="false"].inline-show-more-text__button',
            'button[data-control-name="contact_see_more"]',
        ]
        for name in expandable_button_selectors:
            try:
                self.driver.find_element_by_css_selector(name).click()
            except Exception as error:
                log(log.ERROR, "Do not recognize needed button", error)

        # Use JQuery to click on invisible expandable 'see more...' elements
        self.driver.execute_script(
            'document.querySelectorAll(".lt-line-clamp__ellipsis:not(.lt-line-clamp__ellipsis--dummy) .lt-line-clamp__more").forEach(el => el.click())'
        )

    def sleep(self):
        time.sleep(self.holdup)

    def wait(self, condition):
        return WebDriverWait(self.driver, self.holdup).until(condition)

    def wait_for_element_ready(self, by, selector):
        try:
            """Waits for an element to be ready"""
            return self.wait(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            log(log.DEBUG, "wait_for_element_ready TimeoutException")
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        log(log.INFO, "Stop scrapping process")
