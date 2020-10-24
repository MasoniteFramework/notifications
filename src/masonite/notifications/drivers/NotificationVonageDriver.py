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
        for recipient in recipients:
            payload.update({"to": recipient})
            sms.send_message(payload)

    def get_recipients(self, notifiable, notification):
        """Get recipients which can be defined through notifiable route method.
        It can be one or a list of phone numbers.
            return phone
            return [phone1, phone2]
        """
        recipients = notifiable.route_notification_for("vonage", notification)
        # multiple recipients
        if isinstance(recipients, list):
            _recipients = []
            for recipient in recipients:
                _recipients.append(self._format_phone(recipient))
        else:
            _recipients = [self._format_phone(recipients)]
        return _recipients

    def _format_phone(self, phone):
        # TODO ? or not ?
        return phone