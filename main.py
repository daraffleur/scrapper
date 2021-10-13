from app import scrapping_process
from app.logger import log


DRIVER_TYPE = "chrome"


def main():
    """Start scrapping process"""
    log(log.INFO, "Start scrapping process")
    scrapping_process(DRIVER_TYPE)
    log(log.INFO, "Stop scrapping process")


if __name__ == "__main__":
    main()
