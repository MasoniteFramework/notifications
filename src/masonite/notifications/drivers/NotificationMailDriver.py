"""Mail driver Class."""

from masonite import Queue, Mail
from masonite.queues import ShouldQueue
from masonite.helpers import config
from masonite.drivers import BaseDriver, Mailable
from masonite.app import App

from ..NotificationContract import NotificationContract


class NotificationMailDriver(BaseDriver, NotificationContract):
    _driver = None

    def __init__(self, app: App):
        """Mail Driver Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        self._view = self.app.make("View")

    def send(self, notifiable, notification):
        """Used to send the email and run the logic for sending emails."""
        # build email
        data = self.get_data("mail", notifiable, notification)

        recipients = self.get_recipients(notifiable, notification)
        # if isinstance(self, ShouldQueue):
        #     self.app.make(Queue).push(self.app.make('Mail')
        #                               .driver(driver)
        #                               .to(self._to)
        #                               .subject(self._subject)
        #                               .send, args=(self.template,))

        # data can be a MailComponent or a Mailable
        driver_instance = self.get_mail_driver()
        if isinstance(data, Mailable):
            return driver_instance.mailable(data).to(recipients).send()
        else:
            mail = driver_instance.to(recipients).subject(data._subject)
            reply_to_recipients = self.get_reply_to_recipients(data._reply_to)
            if reply_to_recipients:
                mail = mail.reply_to(reply_to_recipients)
            if data._from:
                mail = mail.send_from(self._format_address(data._from))

            return mail.send(data.template)

    def get_mail_driver(self):
        """Shortcut method to get given mail driver instance."""
        driver = config("mail.driver") if not self._driver else None
        return self.app.make("Mail").driver(driver)

    def get_recipients(self, notifiable, notification):
        """Get recipients which can be defined through notifiable route method.
        return email
        return {email: name}
        return [email1, email2]
        return [{email1: ''}, {email2: name2}]
        """
        recipients = notifiable.route_notification_for("mail", notification)
        # multiple recipients
        if isinstance(recipients, list):
            _recipients = []
            for recipient in recipients:
                _recipients.append(self._format_address(recipient))
        else:
            _recipients = [self._format_address(recipients)]
        return _recipients

    def get_reply_to_recipients(self, reply_to_recipients):
        # multiple recipients
        if isinstance(reply_to_recipients, list):
            _recipients = []
            for recipient in reply_to_recipients:
                _recipients.append(self._format_address(recipient))
        else:
            _recipients = [self._format_address(reply_to_recipients)]
        return _recipients

    def _format_address(self, recipient):
        if isinstance(recipient, str):
            return recipient
        elif isinstance(recipient, tuple):
            if len(recipient) != 2 or not recipient[1]:
                raise ValueError(
                    "route_notification_for_mail() should return a string or a tuple (email, name)"
                )
            return "{1} <{0}>".format(*recipient)

    def driver(self, driver):
        """Specifies the driver to use.

        Arguments:
            driver {string} -- The name of the driver.

        Returns:
            self
        """
        self._driver = driver
        return self
