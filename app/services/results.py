from bs4 import BeautifulSoup
from app.logger import log


class Results:

    attributes = []

    def __init__(self, body):
        self.soup = BeautifulSoup(body, "html.parser")

    def _get_attribute_or_none(self, attribute):
        try:
            return getattr(self, attribute)
        except Exception as error:
            log(log.ERROR, "Failed to get attribute '%s': %s", attribute, error)
            return None

    def convert_to_dict(self):
        values = map(self._get_attribute_or_none, self.attributes)
        return dict(zip(self.attributes, values))

    def __dict__(self):
        return self.to_dict()

    def __eq__(self, that):
        return that.__dict__() == self.__dict__()
