

class BaseComponent(object):

    def __init__(self, level=""):
        self._level = level

    def error(self):
        self._level = "error"
        return self

    def success(self):
        self._level = "success"
        return self

    def level(self):
        return self._level
