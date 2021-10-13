import os
import time

from app.logger import log


STORE_FOLDER_NAME = "data"


class BaseService:
    def __init__(self):
        """holdup: int, optional
        wait such amount of time and then do the action
        (thus LinkedIn does not run captcha)
        """
        self.holdup = 6

        self.setup_data_store()

    def get_holdup_time(self):
        return self.holdup

    def wait(self, delay=None):
        """Wait for delay seconds"""
        delay = self.holdup if delay is None else delay
        time.sleep(delay)

    def setup_data_store(self) -> None:
        if not os.path.exists(STORE_FOLDER_NAME):
            os.makedirs(STORE_FOLDER_NAME)
            log(log.INFO, "%s folder is successfully created", STORE_FOLDER_NAME)
