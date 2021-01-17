from unittest.mock import patch
from masonite.testing import TestCase
from masoniteorm.models import Model

from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import VonageComponent
from src.masonite.notifications.exceptions import VonageInvalidMessage, VonageAPIError


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ["name", "email", "password"]

    def route_notification_for_vonage(self, notification):
        return "33752673234"


def to_vonage(self, notifiable):
    return VonageComponent().text("Welcome!").send_from("123456")


class WelcomeNotification(Notification):
    def to_vonage(self, notifiable):
        return to_vonage(self, notifiable)

    def via(self, notifiable):
        return ["vonage"]


class VonageAPIMock(object):
    @staticmethod
    def send_success():
        return {"hoho": "hihi", "message-count": 1, "messages": [{"status": "0"}]}

    @staticmethod
    def send_error(error="Missing api_key", status=2):
        return {
            "message-count": 1,
            "messages": [{"status": str(status), "error-text": error}],
        }


class TestVonageNotifications(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        # reset objects to default between tests
        WelcomeNotification.to_vonage = to_vonage

    def setUpFactories(self):
        User.create(
            {
                "name": "Joe",
                "email": "user@example.com",
                "password": "secret",
            }
        )

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_notification_should_implements_to_vonage(self):
        del WelcomeNotification.to_vonage
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual(
            "Notification model should implement to_vonage() method.",
            str(err.exception),
        )

    def test_to_vonage_text(self):
        message = VonageComponent().text("Welcome text!")
        self.assertEqual("Welcome text!", message._text)

    def test_to_vonage_send_from(self):
        message = VonageComponent().send_from("3615")
        self.assertEqual("3615", message._from)

    def test_to_vonage_set_unicode(self):
        self.assertEqual("text", VonageComponent()._type)
        message = VonageComponent().set_unicode()
        self.assertEqual("unicode", message._type)

    def test_to_vonage_client_ref(self):
        message = VonageComponent().client_ref("123456")
        self.assertEqual("123456", message._client_ref)

    def test_to_vonage_as_dict(self):
        message = VonageComponent().text("Welcome text!").send_from("123456")
        self.assertDictEqual(
            {
                "text": "Welcome text!",
                "from": "123456",
                "type": "text",
            },
            message.as_dict(),
        )

    def test_to_vonage_as_dict_with_optionals(self):
        message = (
            VonageComponent()
            .text("Welcome text!")
            .send_from("123456")
            .set_unicode()
            .client_ref("AZERTY")
        )
        self.assertDictEqual(
            {
                "text": "Welcome text!",
                "from": "123456",
                "type": "unicode",
                "client-ref": "AZERTY",
            },
            message.as_dict(),
        )

    def test_sending_without_credentials(self):
        user = self.user()
        with self.assertRaises(VonageAPIError) as e:
            user.notify(WelcomeNotification())
        error_message = str(e.exception)
        self.assertIn("Code [2]", error_message)
        self.assertIn("api_key", error_message)

    def test_sending(self):
        user = self.user()
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_success()
            )
            user.notify(WelcomeNotification())

    def test_sending_message_with_string_only(self):
        def to_vonage(self, notifiable):
            return "Welcome"

        WelcomeNotification.to_vonage = to_vonage
        user = self.user()
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_success()
            )
            user.notify(WelcomeNotification())

    @patch.dict("config.notifications.VONAGE", {"sms_from": None})
    def test_sending_raises_exception_when_no_from(self):
        """Here from is not defined (not in global config and not in notification)."""
        # override config to remove from definition
        def to_vonage(self, notifiable):
            return "Welcome"

        WelcomeNotification.to_vonage = to_vonage
        user = self.user()
        with self.assertRaises(VonageInvalidMessage):
            user.notify(WelcomeNotification())

    def test_sending_raises_exception_when_no_to(self):
        user = self.user()
        user.route_notification_for_vonage = lambda n: ""
        with self.assertRaises(VonageInvalidMessage):
            user.notify(WelcomeNotification())

    def test_that_routing_accepts_multiple_numbers(self):
        def route_notification_for_vonage(notification):
            return ["33623456789", "+123 456 789"]

        user = self.user()
        user.route_notification_for_vonage = route_notification_for_vonage
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_success()
            )
            user.notify(WelcomeNotification())

    def test_that_vonage_api_error_code_is_available_when_error(self):
        user = self.user()
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_error("Vonage code message", 12)
            )
            with self.assertRaises(VonageAPIError) as e:
                user.notify(WelcomeNotification())
            error_message = str(e.exception)
            self.assertIn("Code [12]", error_message)
            self.assertIn("Vonage code message", error_message)

    def test_sending_to_anonymous(self):
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_success()
            )
            self.notification.route("vonage", "336534231267").notify(
                WelcomeNotification()
            )
