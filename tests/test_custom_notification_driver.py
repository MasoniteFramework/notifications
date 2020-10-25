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

    # def test_sending_to_anonymous_user(self):
    #     self.notification.route(NotificationVoiceClass, "33456712780").notify(WelcomeNotification())
    #     NotificationVoiceClass.send.assert_called()

    # def test_can_send_to_multiple_drivers_with_custom(self):
    #     class CustomNotification(Notification):

    #         def to_mail(self, notifiable):
    #             return MailComponent().line("Welcome email")

    #         def via(self, notifiable):
    #             return ["mail", NotificationVoiceClass]

    #     user = self.user()
    #     notification = WelcomeNotification()
    #     user.notify(notification)
    #     # check custom notif is sent
    #     NotificationVoiceClass.send.assert_called_with(user, notification)

    # def test_that_class_should_implements_send(self):
    #     class NotificationCustomClass(NotificationContract):
    #         pass
    #     class WelcomeNotification(Notification):
    #         def via(self, notifiable):
    #             return [NotificationCustomClass]
    #     user = self.user()
    #     with self.assertRaises(TypeError):
    #         user.notify(WelcomeNotification())

    # def test_that_class_should_implements_notification_contract(self):
    #     class NotificationCustomClass():
    #         def send(self, notifiable, notification):
    #             pass
    #     class WelcomeNotification(Notification):
    #         def via(self, notifiable):
    #             return [NotificationCustomClass]
    #     user = self.user()
    #     with self.assertRaises(InvalidNotificationType):
    #         user.notify(WelcomeNotification())
