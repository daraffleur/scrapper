import os
from dotenv import load_dotenv

from app.database import Database

from app.services.base import BaseService
from app.services.driver import DriverService
from app.services.cookies import CookiesService, PATH_TO_COOKIES
from app.services.scrapper import ScrapperService
from app.services.search import SearchService
from app.services.auth import AuthService

from app.logger import log


load_dotenv()

LINKEDIN_BASE_URL = "https://www.linkedin.com/"
LINKEDIN_USERNAME = os.environ.get("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
JOB_KEYWORD = "Data Science Manager"
# PROFILE_TOOL_KEYWORD = "python developer"
PROFILE_TOOL_KEYWORD = "graphql python developer java net promoter score "


def scrapping_process(driver_type):
    """Set up db connection and open cursor"""
    db = Database()
    db.create_linked_in_profiles_table()

    """Initialize services"""
    base_service = BaseService()
    driver_service = DriverService(driver_type)

    driver = driver_service.get_driver()  # current driver
    holdup = base_service.get_holdup_time()

    cookies_service = CookiesService(driver)
    auth_service = AuthService(driver, holdup, LINKEDIN_BASE_URL)
    search_service = SearchService(driver, holdup, LINKEDIN_BASE_URL)
    scrapper_service = ScrapperService(driver, holdup, LINKEDIN_BASE_URL)

    try:
        """Choose way of loggining to LinkedIn"""
        if os.path.exists(PATH_TO_COOKIES):
            driver.get(LINKEDIN_BASE_URL)
            cookies_service.load_cookies()
            driver.get(LINKEDIN_BASE_URL)
        else:
            auth_service.login_to_linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
            cookies_service.save_cookies()

        """Search profiles"""
        search_service.search_linkedin_profiles(PROFILE_TOOL_KEYWORD)
        base_service.wait()

        """Get list of profiles` links"""
        profile_links = search_service.get_related_profiles_links()
        base_service.wait()

        for link in profile_links:
            """Check if profile has already scrapped"""
            if not db.profile_is_already_scrapped(link):
                """Scrape profile by link"""
                [name, desc, location] = scrapper_service.scrape_profile(link)
                data = (link, name, desc, location)
                db.insert_profile(data)
                log(log.INFO, "New profile is added to DB")

        base_service.wait()

        log(log.INFO, "Done scrapping")

    except Exception as error:
        log(log.ERROR, error)
    finally:
        conn = db.get_connection()
        if conn:
            log(log.INFO, "Close connection to db")
            db.close_cursor()
            db.close_connection_to_db(conn)
        driver_service.close_driver_session()
