import time

from bs4 import BeautifulSoup


class ScrapperService:
    def __init__(self, driver, holdup: int, linkedin_base_url: str):
        self.driver = driver
        self.holdup = holdup
        self.linkedin_base_url = linkedin_base_url

    def scroll_profile_page(self):
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

    def get_full_name(self, intro):
        """Extract profile name"""
        name_loc = intro.find("h1")
        return name_loc.get_text().strip()

    def get_description(self, intro):
        """Extract profile description"""
        desc_loc = intro.find("div", {"class": "text-body-medium"})
        return desc_loc.get_text().strip()

    def get_location(self, intro):
        """Extract location"""
        location_loc = intro.find_all("span", {"class": "text-body-small"})
        return location_loc[1].get_text().strip()

    def scrape_profile(self, link):
        self.driver.get(link)
        self.scroll_profile_page()

        html = self.driver.page_source
        soup = BeautifulSoup(html, "lxml")

        """
        Extracting the HTML of the complete introduction box
        that contains the name, description, and the location
        """
        introduction = soup.find("div", {"class": "pv-text-details__left-panel"})
        print(introduction)

        name = self.get_full_name(introduction)
        description = self.get_description(introduction)
        location = self.get_location(introduction)

        return [name, description, location]
