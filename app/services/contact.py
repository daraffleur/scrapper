from selenium.webdriver.common.by import By

from app.logger import log
from app.services import Profile
from app.scrappers.scrapper import Scrapper
from app.utils import INVITE_MESSAGE, MAIN_SELECTOR, ERROR_SELECTOR


class ContactService(Scrapper):
    def check_contact_info(self):
        self.maximize_window()
        links = self.db.get_links_of_added_contacts()
        for (link, profile_url) in links:
            self.get_url(link)

            """Wait for page to load dynamically via javascript"""
            self.wait_page_load_dynamically(MAIN_SELECTOR, ERROR_SELECTOR)

            """Check if we got the 'profile unavailable' page"""
            try:
                self.find_element_by_css_selector(MAIN_SELECTOR)
            except Exception as error:
                raise ValueError(
                    "Profile unavailable: Profile link does not match any current Linkedin Profiles",
                    error,
                )
            contact_info = self.get_contact_info()
            profile = Profile(contact_info)
            personal_info = profile.personal_info
            """Parse personal Info"""
            email = personal_info["email"]
            phone = personal_info["phone"]
            connected = personal_info["connected"]
            birth = personal_info["birth"]
            address = personal_info["address"]
            twitter = personal_info["twitter"]
            websites = personal_info["websites"]
            data = (
                email,
                phone,
                connected,
                birth,
                address,
                twitter,
                websites,
            )
            print("DATA TO UPDATE: ", data)
            self.db.update_profile_contact_info_data(data, profile_url)
            log(log.INFO, "Updated contact data for profile: %s", profile_url)

    def scrape_or_check(self):
        self.maximize_window()
        links = self.db.get_profiles_with_empty_email()
        # links = [
        #     (
        #         "https://www.linkedin.com/in/dana-romaniuk/",
        #         "linkedin.com/in/dana-romaniuk/",
        #     )
        # ]
        (number_of_contacts_added_today,) = self.db.get_number_of_contacts_added_today()
        if number_of_contacts_added_today <= 80:
            for link in links:
                full_link, profile_link = link[0], link[1]
                if not self.db.contact_is_already_scrapped(full_link):
                    self.get_url(full_link)
                    self.wait_for_element_ready(By.CLASS_NAME, "pvs-profile-actions")
                    make_contact_button = self.find_element_by_xpath(
                        "//button[@data-control-name='connect']"
                    )
                    if make_contact_button:
                        make_contact_button.click()

                        """Send personalized msg"""
                        personalize_button = self.find_element_by_xpath(
                            "//button[@aria-label='Персонализировать']"
                        )
                        personalize_button.click()
                        self.wait_for_element_ready(
                            By.CLASS_NAME, "connect-button-send-invite__custom-message"
                        )
                        self.sleep()

                        """Enter msg"""
                        input_msg_bar = self.find_element_by_class_name(
                            "connect-button-send-invite__custom-message"
                        )
                        input_msg_bar.send_keys(INVITE_MESSAGE)
                        self.sleep()
                        send_msg_button = self.find_element_by_xpath(
                            "//button[@aria-label='Отправить сейчас']"
                        )
                        self.driver.execute_script(
                            "arguments[0].click();", send_msg_button
                        )
                        self.sleep()
                        data = (full_link, profile_link)
                        self.db.insert_contact(data)
                        self.sleep()
                        log(
                            log.INFO,
                            "The connection request has send to the contact: %s ",
                            link,
                        )
                    else:
                        log(log.INFO, "Can only follow this contact: %s ", link)

        else:
            log(log.INFO, "The limit of connections per today is reached!")
