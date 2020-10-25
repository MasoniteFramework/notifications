import responses
from masonite.testing import TestCase

from config.database import Model
from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import SlackComponent
from src.masonite.notifications.exceptions import (
    NotificationFormatError,
    SlackChannelArchived,
    SlackChannelNotFound,
    SlackInvalidMessage,
)


webhook_url = (
    "https://hooks.slack.com/services/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"
)


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ["name", "email", "password"]

    def route_notification_for_slack(self, notification):
        return webhook_url


def to_slack(self, notifiable):
    return SlackComponent().text("Welcome!")


class WelcomeNotification(Notification):
    def to_slack(self, notifiable):
        return to_slack(self, notifiable)

    def via(self, notifiable):
        return ["slack"]


class TestSlackNotifications(TestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        # reset objects to default between tests
        WelcomeNotification.to_slack = to_slack

    def setUpFactories(self):
        User.create({"name": "Joe", "email": "user@example.com", "password": "secret"})

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_notification_should_implements_to_slack(self):
        del WelcomeNotification.to_slack
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual(
            "Notification model should implement to_slack() method.", str(err.exception)
        )

    @responses.activate
    def test_slack_notification_can_use_dry(self):
        responses.add(responses.POST, webhook_url, body=b"ok")
        user = self.user()
        user.notify(WelcomeNotification().dry())
        # check that Slack webhook not triggered
        self.assertTrue(responses.assert_call_count(webhook_url, 0))

    @responses.activate
    def test_slack_notification_can_fail_silently(self):
        responses.add(
            responses.POST, webhook_url, body=b"channel_not_found", status=404
        )
        user = self.user()
        user.notify(WelcomeNotification().fail_silently())
        # no exception is raised here :)

    def test_to_slack_text(self):
        message = SlackComponent().text("Welcome text!")
        self.assertIn("Welcome text!", message._text)

    def test_to_slack_to(self):
        message = SlackComponent().to("#general")
        self.assertIn("#general", message._channel)
        message = SlackComponent().to("@samuel")
        self.assertIn("@samuel", message._channel)

    def test_to_slack_to_without_prefix(self):
        with self.assertRaises(NotificationFormatError):
            SlackComponent().to("general")

    def test_to_slack_send_from(self):
        message = SlackComponent().send_from("Sam")
        self.assertEqual("Sam", message._username)
        self.assertEqual(None, message._icon_emoji)
        message = SlackComponent().send_from("Sam", ":ghost:")
        self.assertEqual("Sam", message._username)
        self.assertEqual(":ghost:", message._icon_emoji)

    def test_to_slack_link_names(self):
        self.assertEqual(0, SlackComponent()._link_names)
        message = SlackComponent().link_names()
        self.assertEqual(1, message._link_names)

    def test_to_slack_serialization(self):
        message = (
            SlackComponent()
            .success()
            .send_from("test-bot", ":ghost:")
            .to("#general")
            .text("Hello !")
        )
        self.assertDictEqual(
            {
                "text": "Hello !",
                "attachments": [],
                "username": "test-bot",
                "icon_emoji": ":ghost:",
                "channel": "#general",
                "link_names": 0,
                "unfurl_links": False,
                "unfurl_media": False,
            },
            message.as_dict(),
        )

    @responses.activate
    def test_sending_via_webhook(self):
        # mock slack response with success
        responses.add(responses.POST, webhook_url, body=b"ok")
        user = self.user()
        user.notify(WelcomeNotification())

    @responses.activate
    def test_sending_to_invalid_channel(self):
        responses.add(
            responses.POST, webhook_url, body=b"channel_not_found", status=404
        )
        user = self.user()
        with self.assertRaises(SlackChannelNotFound):
            user.notify(WelcomeNotification())

    @responses.activate
    def test_sending_to_archived_channel(self):
        responses.add(
            responses.POST, webhook_url, body=b"channel_is_archived", status=403
        )
        user = self.user()
        with self.assertRaises(SlackChannelArchived):
            user.notify(WelcomeNotification())

    @responses.activate
    def test_sending_malformed_payload(self):
        # this should not happen with components provided, just for checking raising exception
        responses.add(responses.POST, webhook_url, body=b"invalid_payload", status=400)
        user = self.user()
        with self.assertRaises(SlackInvalidMessage):
            user.notify(WelcomeNotification())

    @responses.activate
    def test_sending_too_many_attachments(self):
        responses.add(
            responses.POST, webhook_url, body=b"too_many_attachments", status=400
        )
        user = self.user()
        with self.assertRaises(SlackInvalidMessage):
            user.notify(WelcomeNotification())

    # TODO : add other exceptions

    # Integration test
    def test_sending_complex_message_via_webhook(self):
        user = self.user()

        def to_slack(self, notifiable):
            return (
                SlackComponent()
                .success()
                .send_from("test-bot", ":ghost:")
                .text("Hello @Samuel")
                .link_names()
                .unfurl_links()
            )
            # .text("Hello: https://slack.com/") \

        WelcomeNotification.to_slack = to_slack
        user.notify(WelcomeNotification())

    # @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    # def test_sending_to_anonymous(self, mock_stderr):
    #     self.notification.route("mail", "test@mail.com").notify(CustomNotification())
    #     self.assertIn('To: test@mail.com', mock_stderr.getvalue())
    #     self.assertIn('Welcome!', mock_stderr.getvalue())
