import io
import unittest
import unittest.mock
import responses
from masonite.drivers import BroadcastPusherDriver
from masonite.managers import BroadcastManager

from .UserTestCase import UserTestCase
from src.masonite.notifications import Notification
from src.masonite.notifications.components import MailComponent, SlackComponent, \
    VonageComponent


webhook_url = "https://hooks.slack.com/services/X/Y"


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
    def test_sending_dry_notification_on_notification_class(self, mock_stderr):
        class WelcomeNotification(Notification):

            def to_mail(self, notifiable):
                return MailComponent().subject('Welcome')

            def via(self, notifiable):
                return ["mail"]

        user = self.user()
        user.notify(WelcomeNotification().dry())
        self.assertEqual("", mock_stderr.getvalue())

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_sending_dry_notification_on_notification_interface(self, mock_stderr):
        user = self.user()
        self.notification.send(user, WelcomeNotification("sam"), dry=True)
        self.assertEqual('', mock_stderr.getvalue())

    def test_sending_notification_failing_silently_on_notification_class(self):
        class WelcomeNotification(Notification):

            def to_mail(self, notifiable):
                raise Exception("Mock exception when sending")

            def via(self, notifiable):
                return ["mail"]

        user = self.user()
        user.notify(WelcomeNotification().fail_silently())
        # no exception raised

    def test_sending_fail_silently_notification_on_notification_interface(self):
        class FailingNotification(Notification):

            def to_mail(self, notifiable):
                return Exception("Mock test error")

            def via(self, notifiable):
                return ["mail"]
        user = self.user()
        self.notification.send(user, FailingNotification(), fail_silently=True)
        # no exception raised

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    @responses.activate
    def test_notifications_with_multiple_channels_in_via(self, mock_stderr):
        responses.add(responses.POST, webhook_url, body=b'ok')
        class WelcomeNotification(Notification):

            def to_mail(self, notifiable):
                return MailComponent().subject('Welcome')

            def to_broadcast(self, notifiable):
                return {"message": "Welcome"}

            def to_database(self, notifiable):
                return {"message": "Welcome"}

            def to_slack(self, notifiable):
                return SlackComponent().text("Welcome")

            def to_vonage(self, notifiable):
                return VonageComponent().text("Welcome")

            def broadcast_on(self):
                return "all"

            def via(self, notifiable):
                return ["mail", "broadcast", "database", "slack", "vonage"]

        user = self.user()
        user.route_notification_for_slack = lambda n: webhook_url
        user.notify(WelcomeNotification(), fail_silently=True)
        # check email driver
        self.assertIn("Welcome", mock_stderr.getvalue())
        # check database driver
        self.assertEqual(1, user.notifications().count())
        # check slack driver
        self.assertTrue(responses.assert_call_count(webhook_url, 1))
        # TODO: check broadcast driver ? how

        # TODO: check vonage driver
