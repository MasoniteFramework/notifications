from masonite.drivers import BaseDriver
from unittest.mock import MagicMock

from .UserTestCase import UserTestCase
from src.masonite.notifications import Notification, NotificationContract
from src.masonite.notifications.components import MailComponent
from src.masonite.notifications.exceptions import InvalidNotificationType


class NotificationVoiceDriver(BaseDriver, NotificationContract):
    """Custom notification driver for testing purposes."""

    def send(self, notifiable, notification):
        pass

# the custom class should implements send(notifiable, notification)
NotificationVoiceDriver.send = MagicMock(return_value=True)


class WelcomeNotification(Notification):

    def via(self, notifiable):
        return ["voice"]


class TestCustomDriverNotRegistered(UserTestCase):

    def test_sending_should_fail_when_driver_not_registered(self):
        user = self.user()
        with self.assertRaises(InvalidNotificationType) as e:
            user.notify(WelcomeNotification())
        self.assertIn("voice notification driver has not been found", str(e.exception))


class TestCustomDriver(UserTestCase):
    """Test that custom notifications drivers can be used in an application."""

    def setUp(self):
        super().setUp()
        # register the custom notification driver
        self.container.bind("NotificationVoiceDriver", NotificationVoiceDriver)

    def test_sending(self):
        user = self.user()
        notification = WelcomeNotification()
        user.notify(notification)
        NotificationVoiceDriver.send.assert_called_with(user, notification)

    def test_sending_to_anonymous_user(self):
        self.notification.route("voice", "33456712780").notify(WelcomeNotification())
        NotificationVoiceDriver.send.assert_called()
