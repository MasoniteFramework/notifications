"""Vonage Component Class"""
from .BaseComponent import BaseComponent


class VonageComponent(BaseComponent):

    _from = ""
    _text = ""
    _type = None
    _types = ["text", "binary", "wappush", "unicode", "vcal", "vcard"]

    def send_from(self, number):
        """Numbers are specified in E.164 format."""
        self._from = number
        return self

    def text(self, text):
        self._text = text
        return self

    def sms_type(self, type_key):
        """Choose between text, binary, wappush, unicode, vcal or vcard."""
        if type_key not in self._type:
            raise ValueError("SMS type is incorrect. Should be equal to one of: {0}".format(",".join(self._types)))
        self._type = type_key
        return self

    def as_dict(self):
        base_dict = {
            "from": self._from,
            "text": self._text,
        }
        if self._type:
            base_dict.update({"type": self._type})
        return base_dict
