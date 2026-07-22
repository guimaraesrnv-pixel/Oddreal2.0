from datetime import datetime


class Helpers:

    @staticmethod
    def now():

        return datetime.now()

    @staticmethod
    def timestamp():

        return datetime.now().isoformat()
