import time


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

    def scrape_profile(self, link):
        self.driver.get(link)
        self.scroll_profile_page()
