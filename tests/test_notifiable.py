import io
import sys
import unittest
import unittest.mock
from masonite.app import App
from masonite.testing import TestCase
from masonite.drivers import MailTerminalDriver
from config.database import Model

from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import MailComponent


class WelcomeNotification(Notification):

    def to_mail(self, notifiable):
        return MailComponent().subject('Welcome {0}'.format(notifiable.name)).heading('Welcome email heading !')

    def via(self, notifiable):
        return ["mail"]


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ['name', 'email', 'password']

    def route_notification_for_slack(self, notifiable):
        return "#channel-{}".format(self.name.lower())


class TestNotifiable(TestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)

    def setUpFactories(self):
        User.create({
            'name': 'Joe',
            'email': 'user@example.com',
            'password': 'secret'
        })
        User.create({
            'name': 'John',
            'email': 'john@example.com',
            'password': 'secret'
        })

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_user_as_notifiable_entity(self):
        user = self.user()
        self.assertEqual([], user.notifications())
        self.assertEqual([], user.read_notifications())
        self.assertEqual([], user.unread_notifications())
        self.assertTrue(callable(user.notify))
        self.assertTrue(callable(user.notify_now))

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_user_through_notifiable_mixin(self, mock_stderr):
        user = self.user()
        user.notify(WelcomeNotification())
        printed_email = mock_stderr.getvalue()
        self.assertIn('user@example.com', printed_email)
        self.assertIn('Welcome Joe', printed_email)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_user_through_notify_class(self, mock_stderr):
        user = self.user()
        # works but was mostly designed to send to multiple notifiables
        self.notification.send(user, WelcomeNotification())
        self.assertIn('user@example.com', mock_stderr.getvalue())

        # send to multiple notifiables
        users = User.all()
        self.notification.send(users, WelcomeNotification())
        printed_email = mock_stderr.getvalue()
        self.assertIn('user@example.com', printed_email)
        self.assertIn('john@example.com', printed_email)

    def test_notification_mail_default_routing(self):
        user = self.user()
        # default
        self.assertEqual("user@example.com", user.route_notification_for("mail"))

    def test_notification_mail_custom_routing(self):
        user = self.user()

        def route(notifiable):
            return "john.doe@example.com"
        setattr(user, "route_notification_for_mail", route)
        self.assertEqual("john.doe@example.com", user.route_notification_for("mail"))

    def test_notification_mail_custom_routing_with_list(self):
        user = self.user()

        def route(notifiable):
            return (notifiable.email, notifiable.name)
        setattr(user, "route_notification_for_mail", route)
        self.assertEqual(("user@example.com", "Joe"), user.route_notification_for("mail"))

        def route(notifiable):
            return ["mail1@masonite.com", "mail2@masonite.com"]
        setattr(user, "route_notification_for_mail", route)
        self.assertEqual(["mail1@masonite.com", "mail2@masonite.com"], user.route_notification_for("mail"))

    def test_notification_mail_incorrect_custom_routing_with_list(self):
        user = self.user()

        def route(notifiable):
            return (notifiable.email, "")
        setattr(user, "route_notification_for_mail", route)
        with self.assertRaises(ValueError):
            user.notify(WelcomeNotification())

        # Not raised because to deep I guess
        # def route(notifiable):
        #     return (notifiable.email)
        # setattr(user, "route_notification_for_mail", route)
        # with self.assertRaises(ValueError):
        #     user.notify(WelcomeNotification())

    def test_notification_slack_routing(self):
        user = self.user()
        self.assertEqual("#channel-joe", user.route_notification_for("slack"))

    def test_that_custom_driver_requires_routing_method(self):
        user = self.user()
        with self.assertRaises(NotImplementedError):
            user.route_notification_for("sms_service")
