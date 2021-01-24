import json
import pytest
import responses
from masonite.testing import TestCase
from masonite import env
from masoniteorm.models import Model
from slackblocks import DividerBlock, HeaderBlock

from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import SlackComponent
from src.masonite.notifications.exceptions import (
    NotificationFormatError,
    SlackChannelArchived,
    SlackChannelNotFound,
    SlackInvalidMessage,
)

# fake webhook for tests
webhook_url = "https://hooks.slack.com/services/X/Y/Z"


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
    sqlite = False

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

    def test_to_slack_send_from(self):
        message = SlackComponent().send_from("Sam")
        self.assertEqual("Sam", message._username)
        self.assertEqual("", message._icon_emoji)
        message = SlackComponent().send_from("Sam", ":ghost:")
        self.assertEqual("Sam", message._username)
        self.assertEqual(":ghost:", message._icon_emoji)
        message = SlackComponent().send_from("Sam", url="#")
        self.assertEqual("Sam", message._username)
        self.assertEqual("", message._icon_emoji)
        self.assertEqual("#", message._icon_url)

    def test_to_slack_token(self):
        message = SlackComponent().token("123")
        self.assertEqual("123", message._token)

    def test_to_slack_as_current_user(self):
        message = SlackComponent().as_current_user()
        self.assertTrue(message._as_current_user)

    def test_to_slack_without_markdown(self):
        message = SlackComponent().without_markdown()
        self.assertFalse(message._mrkdwn)

    def test_to_slack_can_reply(self):
        message = SlackComponent().can_reply()
        self.assertTrue(message._reply_broadcast)

    def test_to_slack_link_names(self):
        self.assertFalse(SlackComponent()._link_names)
        message = SlackComponent().link_names()
        self.assertTrue(message._link_names)

    def test_to_slack_block(self):
        message = SlackComponent()
        self.assertEqual([], message._blocks)
        block = DividerBlock()
        message = message.block(block)
        self.assertEqual([block], message._blocks)
        block2 = HeaderBlock("title")
        self.assertEqual([block, block2], message.block(block2)._blocks)
        with self.assertRaises(NotificationFormatError):
            message.block("test")

    def test_to_slack_as_dict(self):
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
                "channel": "#general",
                "link_names": False,
                "unfurl_links": False,
                "username": "test-bot",
                "unfurl_media": False,
                "as_user": False,
                "icon_emoji": ":ghost:",
                "icon_url": "",
                "mrkdwn": True,
                "reply_broadcast": False,
                "blocks": json.dumps([]),
            },
            message.as_dict(),
        )

    @responses.activate
    def test_sending_via_webhook(self):
        # mock slack response with success
        responses.add(responses.POST, webhook_url, body=b"ok")
        user = self.user()
        user.notify(WelcomeNotification())
        self.assertTrue(responses.assert_call_count(webhook_url, 1))

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

    # Integration
    @pytest.mark.skipif(
        not env("SLACK_TOKEN"),
        reason="Skip real Slack test because SLACK_TOKEN env variable not set.",
    )
    def test_sending_complex_message_via_webhook(self):
        User.route_notification_for_slack = lambda self, notifiable: "#bot"
        user = self.user()

        def to_slack(self, notifiable):
            return SlackComponent().send_from("masonite-notifications").text("Hello !")

        WelcomeNotification.to_slack = to_slack
        # send to user
        user.notify(WelcomeNotification())
        # send anonymous
        self.notification.route("slack", "#bot").notify(WelcomeNotification())

    @responses.activate
    def test_sending_to_anonymous(self):
        responses.add(responses.POST, webhook_url, body=b"ok")
        self.notification.route("slack", webhook_url).notify(WelcomeNotification())
        self.assertTrue(responses.assert_call_count(webhook_url, 1))


class TestSlackNotificationsFormatting(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        # reset objects to default between tests
        WelcomeNotification.to_slack = to_slack

    def test_build_basic_notifications(self):
        message = (
            SlackComponent()
            .send_from("Sam")
            .to("#bot")
            .text("Hello")
            .link_names()
            .without_markdown()
            .can_reply()
        )

        self.assertEqual(
            {
                "text": "Hello",
                "channel": "#bot",
                "link_names": True,
                "unfurl_links": False,
                "unfurl_media": False,
                "username": "Sam",
                "as_user": False,
                "icon_emoji": "",
                "icon_url": "",
                "mrkdwn": False,
                "reply_broadcast": True,
                "blocks": json.dumps([]),
            },
            message.as_dict(),
        )

    def test_build_notifications_with_blocks(self):
        message = (
            SlackComponent()
            .send_from("Sam")
            .text("Hello")
            .block(HeaderBlock("Header title", block_id="1"))
            .block(DividerBlock(block_id="2"))
        )
        self.assertEqual(
            {
                "text": "Hello",
                "channel": "",
                "link_names": False,
                "unfurl_links": False,
                "unfurl_media": False,
                "username": "Sam",
                "as_user": False,
                "icon_emoji": "",
                "icon_url": "",
                "mrkdwn": True,
                "reply_broadcast": False,
                "blocks": '[{"type": "header", "block_id": "1", "text": {"type": "plain_text", "text": "Header title"}}, {"type": "divider", "block_id": "2"}]',
            },
            message.as_dict(),
        )
