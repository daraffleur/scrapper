from selenium.webdriver.common.by import By

from app.scrappers.scrapper import Scrapper
from app.utils import INVITE_MESSAGE


class ContactService(Scrapper):
    def scrape_or_check(self):
        self.maximize_window()
        # links = self.db.get_profiles_with_empty_email()
        links = ["https://www.linkedin.com/in/dana-romaniuk/"]
        for link in links:
            if not self.db.contact_is_already_scrapped(link):
                self.get_url(link)
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
                    self.driver.execute_script("arguments[0].click();", send_msg_button)
                    self.sleep()
                    data = (link,)
                    self.db.insert_contact(data)
