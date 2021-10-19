import os
import click

# from click import ClickException
from dotenv import load_dotenv

from app.database import Database
from app.scrappers import ProfileLinksScrapper
from app.services import DriverService, CookiesService, AuthService
from app.utils import HEADLESS_OPTIONS, PATH_TO_COOKIES, LINKEDIN_BASE_URL

from app.logger import log


load_dotenv()

LINKEDIN_USERNAME = os.environ.get("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")


@click.command()
@click.option(
    "-username",
    type=str,
    required=True,
    help="Enter email or username of profile: ",
    default=LINKEDIN_USERNAME,
)
@click.option(
    "-password",
    type=str,
    required=True,
    help="Enter password: ",
    default=LINKEDIN_PASSWORD,
)
@click.option(
    "-action_type",
    type=click.Choice(["collect_links", "scrape collected profiles"]),
    required=True,
    help="Check type of action: ",
    default="collect_links",
)
@click.option(
    "-search_keyword",
    type=str,
    required=False,
    help="Enter search query (e.g. python developer): ",
    default="graphql python developer java net promoter score ",
)
# @click.option(
#     "--headless", is_flag=True, help="Run in headless mode (Press enter to skip)"
# )
@click.option(
    "--driver",
    type=click.Choice(["Chrome", "Firefox"]),
    help="Webdriver to use: (Chrome/Firefox)",
    default="Chrome",
)
def scrape(username, password, action_type, search_keyword, driver):
    search_keyword = "graphql python developer java net promoter score"
    log(log.INFO, "Start scrapping process")
    with DriverService(driver) as driver_service:
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
            auth_service.login_to_linkedin(username, password)
            cookies_service.save_cookies()

        with Database() as db:
            """Set up db connection and open cursor"""
            db.create_linked_in_profiles_table()

            with ProfileLinksScrapper(
                db,
                driver=driver,
                # driver_options=driver_options,
            ) as scraper:
                scraper.scrape(search_keyword)


if __name__ == "__main__":
    scrape()
