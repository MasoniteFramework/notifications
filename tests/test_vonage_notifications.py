import responses
from masonite.testing import TestCase

from config.database import Model
from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import NexmoComponent
from src.masonite.notifications.exceptions import NexmoInvalidMessage


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ['name', 'email', 'password']

    def route_notification_for_nexmo(self, notification):
        return "+33123456789"


def to_nexmo(self, notifiable):
    return NexmoComponent().text("Welcome!").send_from("123456")


class WelcomeNotification(Notification):

    def to_nexmo(self, notifiable):
        return to_nexmo(self, notifiable)

    def via(self, notifiable):
        return ["nexmo"]


class TestNexmoNotifications(TestCase):

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        # reset objects to default between tests
        WelcomeNotification.to_nexmo = to_nexmo

    def setUpFactories(self):
        User.create({
            'name': 'Joe',
            'email': 'user@example.com',
            'password': 'secret',
        })

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_notification_should_implements_to_nexmo(self):
        del WelcomeNotification.to_nexmo
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual("Notification model should implement to_nexmo() method.",
                         str(err.exception))

    def test_to_nexmo_text(self):
        message = NexmoComponent().text('Welcome text!')
        self.assertEqual('Welcome text!', message._text)

    def test_to_nexmo_send_from(self):
        message = NexmoComponent().send_from("3615")
        self.assertEqual('3615', message._from)

    def test_to_nexmo_set_unicode(self):
        self.assertEqual("text", NexmoComponent()._type)
        message = NexmoComponent().set_unicode()
        self.assertEqual("unicode", message._type)

    def test_to_nexmo_client_ref(self):
        message = NexmoComponent().client_ref("123456")
        self.assertEqual("123456", message._client_ref)

    def test_to_nexmo_as_dict(self):
        message = NexmoComponent() \
            .text('Welcome text!') \
            .send_from("Sam")
        self.assertDictEqual({
            "text": "Welcome text!",
            "from": "123456",
            "type": "text",
        })

    def test_to_nexmo_as_dict_with_optionals(self):
        message = NexmoComponent() \
            .text('Welcome text!') \
            .send_from("123456") \
            .set_unicode() \
            .client_ref("AZERTY")
        self.assertDictEqual({
            "text": "Welcome text!",
            "from": "123456",
            "type": "unicode",
            "client-ref": "AZERTY"
        })

    def test_sending_sms_via_nexmo(self):
        user = self.user()
        user.notify(WelcomeNotification())

    def test_sending_raises_exception_when_no_from_or_to(self):
        pass

    def test_that_routing_accepts_multiple_numbers(self):
        def to_nexmo(notifiable):
            return ["+33123456789", "+123 456 789"]
        WelcomeNotification.to_nexmo = to_nexmo
        user = self.user()
        user.notify(WelcomeNotification())