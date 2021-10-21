import os

from dotenv import load_dotenv

from app.database import Database
from app.services import ContactService, DriverService, AuthService, CookiesService
from app.utils import PATH_TO_COOKIES, LINKEDIN_BASE_URL


load_dotenv()

LINKEDIN_USERNAME = os.environ.get("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")


def check_contact():
    with DriverService("Chrome") as driver_service:
        """Open selenium driver session"""
        driver = driver_service.get_driver()

        cookies_service = CookiesService(driver)
        auth_service = AuthService(driver)

        """Choose way of loggining to LinkedIn"""
        if os.path.exists(PATH_TO_COOKIES):
            driver.get(LINKEDIN_BASE_URL)
            cookies_service.load_cookies()
            driver.get(LINKEDIN_BASE_URL)
        else:
            auth_service.login_to_linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
            cookies_service.save_cookies()

        with Database() as db:
            """Set up db connection and open cursor"""
            db.create_linked_in_profiles_table()

            with ContactService(
                db,
                driver=driver,
                # driver_options=driver_options,
            ) as scraper:
                scraper.scrape_or_check()


if __name__ == "__main__":
    check_contact()
