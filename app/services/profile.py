# from typing import List

from bs4 import BeautifulSoup

# from app.logger import log


class Profile:
    """LinkedIn User Profile Object"""

    def __init__(self):
        self.soup = None

    def get_soup(self, html):
        self.soup = BeautifulSoup(html, "lxml")

    def get_contact_info(self, content):
        html = BeautifulSoup(content.get_attribute("innerHTML"), "lxml")

        email = self.get_email(html)
        birth_day = self.get_birth_day(html)
        return [email, birth_day]

    def get_introduction(self):
        name = self.get_full_name()
        description = self.get_description()
        location = self.get_location()
        return [name, description, location]

    def get_email(self, html):
        """Extract email"""
        email_class = html.find("section", {"class": "ci-email"})
        if email_class:
            email_loc = email_class.find("a")
            return email_loc.get_text().strip()
        else:
            return ""

    def get_birth_day(self, html):
        """Extract date of birth"""
        birth_class = html.find("section", {"class": "ci-birthday"})
        if birth_class:
            birth_loc = birth_class.find(
                "span",
            )
            return birth_loc.get_text().strip()
        else:
            return ""

    def get_full_name(self):
        """Extract profile name"""
        introduction = self.soup.find("div", {"class": "pv-text-details__left-panel"})
        name_loc = introduction.find("h1")
        return name_loc.get_text().strip()

    def get_description(self):
        """Extract profile description"""
        introduction = self.soup.find("div", {"class": "pv-text-details__left-panel"})
        desc_loc = introduction.find("div", {"class": "text-body-medium"})
        return desc_loc.get_text().strip()

    def get_location(self):
        """Extract location"""
        location_div = self.soup.find(
            "div", {"class": "pb2 pv-text-details__left-panel"}
        )
        location_loc = location_div.find_all("span", {"class": "text-body-small"})
        return location_loc[0].get_text().strip()
