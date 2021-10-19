from selenium import webdriver

from app.logger import log


class DriverService:
    def __init__(self, driver_type):
        self.driver = None
        self.initialize_driver(driver_type)

    def initialize_driver(self, driver_type):
        if driver_type == "Chrome":
            self.driver = webdriver.Chrome(
                executable_path="drivers/Chrome/chromedriver.exe"
            )  # allow to access webpages from the chrome browser
        else:
            pass  # TODO: add Firefox

    def get_driver(self):
        return self.driver

    def close_driver_session(self):
        log(log.INFO, "Close driver session")
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close_driver_session()
