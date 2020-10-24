"""Vonage driver Class."""
from masonite.drivers import BaseDriver
from masonite.app import App
from masonite.helpers import config

from ..NotificationContract import NotificationContract
from ..exceptions import NexmoInvalidMessage


class NotificationVonageDriver(BaseDriver, NotificationContract):

    def __init__(self, app: App):
        """Vonage Driver Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        import vonage
        self._client = vonage.Client(key=config("notifications.nexmo.key"),
                                     secret=config("notifications.nexmo.secret"))
        self._sms_from = config("notifications.nexmo.sms_from") or None

    def send(self, notifiable, notification):
        """Used to send the SMS and run the logic for sending SMS."""
        data = self.get_data("vonage", notifiable, notification)
        recipients = self.get_recipients(notifiable, notification)
        from vonage.sms import Sms
        sms = Sms(self._client)
        for recipient in recipients:
            payload = self.build_payload(data, recipient)
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
                _recipients.append(recipient)
        else:
            _recipients = [recipients]
        return _recipients

    def build_payload(self, data, recipient):
        """Build SMS payload sent to Vonage API""".
        # define send_from from config if not set
        if not data._from:
            data = data.send_from(self._sms_from)
        payload = {
            **data.as_dict(),
            "to": recipient
        }
        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload):
        """Validate SMS payload before sending by checking that from et to
        are correctly set."""
        if not payload.get("from", None):
            raise NexmoInvalidMessage("from must be specified.")
        if not payload.get("to", None):
            raise NexmoInvalidMessage("to must be specified.")
