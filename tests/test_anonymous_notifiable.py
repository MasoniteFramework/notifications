import unittest
import unittest.mock
from masonite.testing import TestCase

from src.masonite.notifications import NotificationFacade, Notification
from src.masonite.notifications.components import MailComponent
from src.masonite.notifications.AnonymousNotifiable import AnonymousNotifiable


class WelcomeNotification(NotificationFacade):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def to_mail(self, notifiable):
        return (
            MailComponent()
            .subject("Welcome {0}".format(notifiable.name))
            .heading("Welcome email heading !")
        )

    def via(self, notifiable):
        return ["mail"]


class TestAnonymousNotifiable(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notification(self.container)
        self.anon_notifiable = AnonymousNotifiable()

    def test_one_routing(self):
        notifiable = self.anon_notifiable.route("mail", "user@example.com")
        self.assertDictEqual({"mail": "user@example.com"}, notifiable._routes)

    def test_multiple_routing(self):
        notifiable = self.anon_notifiable.route("mail", "user@example.com").route(
            "slack", "#general"
        )
        self.assertDictEqual(
            {"mail": "user@example.com", "slack": "#general"}, notifiable._routes
        )

    def test_that_incorrect_channel_routing_raise_exception(self):
        with self.assertRaises(ValueError) as err:
            self.anon_notifiable.route_notification_for("custom_sms", "+337232323232")
        self.assertEqual(
            "Routing has not been defined for the channel custom_sms",
            str(err.exception),
        )
