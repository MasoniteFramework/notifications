"""Mail notification channel."""

from masonite import Queue, Mail
from masonite.queues import ShouldQueue
from masonite.helpers import config
from masonite.drivers import BaseDriver
from masonite.app import App

from ..exceptions import InvalidNotificationType
from ..NotificationContract import NotificationContract


class NotificationMailDriver(BaseDriver, NotificationContract):
    _driver = None

    def __init__(self, app: App):
        """Mail Component Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        self._view = self.app.make('View')

    def send(self, notifiable, notification):
        """Used to send the email and run the logic for sending emails."""
        driver = config("mail.driver") if not self._driver else None
        # build email
        message = notification.to_mail(notifiable)
        recipients = self.get_recipients(notifiable, notification)
            # if isinstance(self, ShouldQueue):
            #     self.app.make(Queue).push(self.app.make('Mail')
            #                               .driver(driver)
            #                               .to(self._to)
            #                               .subject(self._subject)
            #                               .send, args=(self.template,))
            # else:
        import pdb
        pdb.set_trace()
        self.app.make('Mail') \
            .driver(driver) \
            .to(recipients) \
            .send(message)

    def get_recipients(self, notifiable, notification):
        recipients = notifiable.route_notification_for("mail", notification)
        if isinstance(recipients, str):
            recipients = [recipients]
        return recipients


        """Sets the subject of the email.

        Arguments:
            message {string} -- The text to show as the email header.

        Returns:
            self
        """
        self._subject = message
        return self

    def driver(self, driver):
        """Specifies the driver to use.

        Arguments:
            driver {string} -- The name of the driver.

        Returns:
            self
        """
        self._driver = driver
        return self
