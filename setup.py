from setuptools import setup

VERSION = "1.0"


def readme_file():
    with open("README.md") as f:
        return f.read()


setup(
    name="ScrapperBot",
    version=VERSION,
    description="Selenium Scraper for Linkedin",
    long_description=readme_file(),
    author="Simple2B",
    packages=["app"],
    entry_points={"console_scripts": ["scrape=app.run:scrape"]},
    # install_requires=["beautifulsoup4>=4.6.0", "bs4", "selenium", "click", "joblib"],
)
