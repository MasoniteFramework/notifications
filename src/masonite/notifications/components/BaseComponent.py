class BaseComponent(object):
    def __init__(self, level=""):
        self._level = level
        self._colors = {
            "error": "red",
            "success": "success",
            "warning": "orange",
            "info": "blue",
        }

    def error(self):
        self._level = "error"
        return self

    def success(self):
        self._level = "success"
        return self

    def warning(self):
        self._level = "warning"
        return self

    def info(self):
        self._level = "info"
        return self

    def level(self):
        return self._level

    def color(self):
        """Get message color depending on level"""
        return self._colors.get(self._level, "")
