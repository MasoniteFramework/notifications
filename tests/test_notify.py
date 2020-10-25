import io
import unittest
import unittest.mock
from unittest.mock import MagicMock
import responses
from masonite.drivers import BroadcastPusherDriver
from masonite.managers import BroadcastManager

from .UserTestCase import UserTestCase
from src.masonite.notifications import Notification
from src.masonite.notifications.components import (
    MailComponent,
    SlackComponent,
    VonageComponent,
)
from src.masonite.notifications.drivers import (
    NotificationSlackDriver,
    NotificationMailDriver,
)
from src.masonite.notifications.exceptions import (
    InvalidNotificationType,
    NotificationChannelsNotDefined,
)

webhook_url = "https://hooks.slack.com/services/X/Y"


class WelcomeNotification(Notification):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def to_mail(self, notifiable):
        return (
            MailComponent()
            .subject("Welcome {0}!".format(self.name))
            .heading("Welcome email heading !")
        )

    def via(self, notifiable):
        return ["mail"]


class TestNotifyHandler(UserTestCase):
    def setUp(self):
        super().setUp()
        # tests are made with Pusher driver
        self.container.bind("BroadcastPusherDriver", BroadcastPusherDriver)
        self.container.bind("BroadcastManager", BroadcastManager)

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user(self, mock_stderr):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).notify(WelcomeNotification("John"))
        printed_email = mock_stderr.getvalue()
        self.assertIn("john.doe@masonite.com", printed_email)
        self.assertIn("Welcome John", printed_email)

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user_with_multiple_channels(
        self, mock_stderr
    ):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).route("slack", "#general").notify(
            WelcomeNotification("John")
        )
        # check email notification sent
        printed_email = mock_stderr.getvalue()
        self.assertIn("john.doe@masonite.com", printed_email)
        # TODO: check Slack notification sent ?

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_dry_notification_on_notification_class(self, mock_stderr):
        class WelcomeNotification(Notification):
            def to_mail(self, notifiable):
                return MailComponent().subject("Welcome")

            def via(self, notifiable):
                return ["mail"]

        user = self.user()
        user.notify(WelcomeNotification().dry())
        self.assertEqual("", mock_stderr.getvalue())

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_dry_notification_on_notification_interface(self, mock_stderr):
        user = self.user()
        self.notification.send(user, WelcomeNotification("sam"), dry=True)
        self.assertEqual("", mock_stderr.getvalue())

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

    def test_invalid_notification_driver_in_via_raises_error(self):
        class FailingNotification(Notification):
            def via(self, notifiable):
                return ["incorrect_driver"]

        user = self.user()
        with self.assertRaises(InvalidNotificationType) as e:
            user.notify(FailingNotification())
        self.assertIn(
            "incorrect_driver notification driver has not been found in the container",
            str(e.exception),
        )

    def test_that_empty_via_raises_an_error(self):
        class FailingNotification(Notification):
            def via(self, notifiable):
                return []

        user = self.user()
        with self.assertRaises(NotificationChannelsNotDefined) as e:
            user.notify(FailingNotification())
        self.assertIn(
            "via() method of FailingNotification class.",
            str(e.exception),
        )

    def test_that_channels_can_be_overriden_at_send(self):
        class WelcomeNotification(Notification):
            def to_mail(self, notifiable):
                return "mail"

            def to_slack(self, notifiable):
                return "slack"

            def via(self):
                return ["mail"]

        user = self.user()
        user.route_notification_for_slack = lambda n: "webhook_url"
        slack_send_backup = NotificationSlackDriver.send
        mail_send_backup = NotificationMailDriver.send
        # mock slack send method call
        NotificationSlackDriver.send = MagicMock(return_value="slack")
        NotificationMailDriver.send = MagicMock(return_value="mail")
        user.notify(WelcomeNotification(), channels=["slack"])

        NotificationSlackDriver.send.assert_called()
        NotificationMailDriver.send.assert_not_called()
        NotificationSlackDriver.send = slack_send_backup
        NotificationMailDriver.send = mail_send_backup

    def test_that_channels_can_be_overriden_at_send_with_notification_interface(self):
        class WelcomeNotification(Notification):
            def to_mail(self, notifiable):
                return "mail"

            def to_slack(self, notifiable):
                return "slack"

            def via(self):
                return ["mail"]

        user = self.user()
        user.route_notification_for_slack = lambda n: "webhook_url"
        # allow to revert driver to original version to avoid affecting other tests
        slack_send_backup = NotificationSlackDriver.send
        mail_send_backup = NotificationMailDriver.send
        # mock slack send method call
        NotificationSlackDriver.send = MagicMock(return_value="slack")
        NotificationMailDriver.send = MagicMock(return_value="mail")
        self.notification.send(user, WelcomeNotification(), channels=["slack"])

        NotificationSlackDriver.send.assert_called()
        NotificationMailDriver.send.assert_not_called()
        NotificationSlackDriver.send = slack_send_backup
        NotificationMailDriver.send = mail_send_backup

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    @responses.activate
    def test_notifications_with_multiple_channels_in_via(self, mock_stderr):
        responses.add(responses.POST, webhook_url, body=b"ok")
        # as all requests are mocked unmock the one for Vonage
        responses.add_passthru("https://rest.nexmo.com/sms/json")

        class WelcomeNotification(Notification):
            def to_mail(self, notifiable):
                return MailComponent().subject("Welcome")

            def to_database(self, notifiable):
                return {"message": "Welcome"}

            def to_slack(self, notifiable):
                return SlackComponent().text("Welcome")

            def to_vonage(self, notifiable):
                return VonageComponent().text("Welcome")

            def via(self, notifiable):
                return ["mail", "database", "slack", "vonage"]

        user = self.user()
        user.route_notification_for_slack = lambda n: webhook_url
        user.route_notification_for_vonage = lambda n: "33656789101"

        # mock vonage api
        with unittest.mock.patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = {}
            user.notify(WelcomeNotification())
        # check email driver
        self.assertIn("Welcome", mock_stderr.getvalue())
        # check database driver
        self.assertEqual(1, user.notifications().count())
        # check slack driver
        self.assertTrue(responses.assert_call_count(webhook_url, 1))
