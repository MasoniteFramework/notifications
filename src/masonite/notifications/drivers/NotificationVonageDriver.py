"""Vonage driver Class."""
from masonite.drivers import BaseDriver
from masonite.app import App

from ..NotificationContract import NotificationContract


class NotificationVonageDriver(BaseDriver, NotificationContract):

    def __init__(self, app: App):
        """Vonage Driver Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        import vonage
        # TODO: fetch from config / allow also to fetch directly ?
        self._client = vonage.Client(key="", secret="")

    def send(self, notifiable, notification):
        """Used to send the SMS and run the logic for sending SMS."""
        vonage_component = self.get_data("vonage", notifiable, notification)
        # TODO
        payload = vonage_component.as_dict()
        recipients = self.get_recipients(notifiable, notification)
        from vonage.sms import Sms
        sms = Sms(self._client)
        sms.send_message(payload)