"""Vonage Component Class"""
from .BaseComponent import BaseComponent


class VonageComponent(BaseComponent):

    _from = ""
    _text = ""
    _client_ref = ""
    _type = "text"

    def send_from(self, number):
        """Set the name or number the message should be sent from. Numbers should
        be specified in E.164 format. Details can be found here:
        https://developer.nexmo.com/messaging/sms/guides/custom-sender-id"""
        self._from = number
        return self

    def text(self, text):
        self._text = text
        return self

    def set_unicode(self):
        """Set message as unicode to handle unicode characters in text."""
        self._type = "unicode"
        return self

    def client_ref(self, client_ref):
        """Set your own client reference (up to 40 characters)."""
        if len(client_ref) > 40:
            raise ValueError("client_ref should have less then 40 characters.")
        self._client_ref = client_ref
        return self

    def as_dict(self):
        base_dict = {
            "from": self._from,
            "text": self._text,
        }
        if self._type:
            base_dict.update({"type": self._type})
        if self._client_ref:
            base_dict.update({"client-ref": self._type})
        return base_dict
