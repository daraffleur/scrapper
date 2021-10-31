from setuptools import setup


setup(
    name="ScrapperBot",
    description="Selenium Scraper for Linkedin",
    author="Simple2B",
    packages=["app"],
    entry_points={"console_scripts": ["scrape=run:scrape"]},
)
