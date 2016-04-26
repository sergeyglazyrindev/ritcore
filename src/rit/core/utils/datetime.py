import datetime


class RitDateTime(object):

    @classmethod
    def now(cls):
        return datetime.datetime.now()
