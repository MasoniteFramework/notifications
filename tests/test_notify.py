import io
import unittest
import unittest.mock
from masonite.drivers import BroadcastPusherDriver
from masonite.managers import BroadcastManager

from .UserTestCase import UserTestCase
from src.masonite.notifications import Notification
from src.masonite.notifications.components.MailComponent import MailComponent


class WelcomeNotification(Notification):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def to_mail(self, notifiable):
        return MailComponent().subject('Welcome {0}!'.format(self.name)).heading('Welcome email heading !')

    def via(self, notifiable):
        return ["mail"]


class TestNotifyHandler(UserTestCase):

    def setUp(self):
        super().setUp()
        # tests are made with Pusher driver
        self.container.bind('BroadcastPusherDriver', BroadcastPusherDriver)
        self.container.bind('BroadcastManager', BroadcastManager)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user(self, mock_stderr):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).notify(WelcomeNotification("John"))
        printed_email = mock_stderr.getvalue()
        self.assertIn('john.doe@masonite.com', printed_email)
        self.assertIn('Welcome John', printed_email)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user_with_multiple_channels(self, mock_stderr):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).route("slack", "#general").notify(WelcomeNotification("John"))
        # check email notification sent
        printed_email = mock_stderr.getvalue()
        self.assertIn('john.doe@masonite.com', printed_email)
        # TODO: check Slack notification sent ?

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_sending_dry_notification_does_not_send(self, mock_stderr):
        class WelcomeNotification(Notification):

            def to_mail(self, notifiable):
                return MailComponent().subject('Welcome')

            def via(self, notifiable):
                return ["mail"]

        user = self.user()
        user.notify(WelcomeNotification().dry())
        self.assertEqual("", mock_stderr.getvalue())

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_notifications_with_multiple_channels_in_via(self, mock_stderr):
        class WelcomeNotification(Notification):

            def to_mail(self, notifiable):
                return MailComponent().subject('Welcome')

            def to_broadcast(self, notifiable):
                return {"message": "Welcome"}

            def to_database(self, notifiable):
                return {"message": "Welcome"}

            def broadcast_on(self):
                return "all"

            def via(self, notifiable):
                return ["mail", "broadcast", "database"]

        user = self.user()
        user.notify(WelcomeNotification())
        self.assertIn("Welcome", mock_stderr.getvalue())
        self.assertEqual(1, user.notifications().count())
