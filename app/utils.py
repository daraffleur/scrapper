from selenium.webdriver.chrome.options import Options


STORE_FOLDER_NAME = "data"
FILE_FOR_COOKIES = "cookies.txt"
LINKEDIN_BASE_URL = "https://www.linkedin.com/"
PATH_TO_COOKIES = f"{STORE_FOLDER_NAME}/{FILE_FOR_COOKIES}"

options = Options()
options.add_argument("--headless")
HEADLESS_OPTIONS = {"chrome_options": options}
