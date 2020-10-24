"""Nexmo driver Class."""
from masonite.drivers import BaseDriver
from masonite.app import App

from ..NotificationContract import NotificationContract


class NotificationNexmoDriver(BaseDriver, NotificationContract):

    def __init__(self, app: App):
        """Nexmo Driver Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app

    def send(self, notifiable, notification):
        """Used to send the SMS and run the logic for sending SMS."""
        # build email
        data = self.get_data("nexmo", notifiable, notification)
        recipients = self.get_recipients(notifiable, notification)