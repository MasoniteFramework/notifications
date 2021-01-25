import io
import responses
from masonite.testing import TestCase
import unittest
import unittest.mock
from unittest.mock import patch
from masonite.drivers import QueueAsyncDriver, BroadcastPusherDriver
from masonite.managers import QueueManager, BroadcastManager
from masonite.queues import ShouldQueue
from masonite.app import App
from masonite.environment import LoadEnvironment

from src.masonite.notifications.drivers import NotificationBroadcastDriver
from src.masonite.notifications import Notification
from src.masonite.notifications.components import (
    MailComponent,
    SlackComponent,
    VonageComponent,
)
from .test_mail_notifications import WelcomeNotification as MailNotification
from .test_broadcast_notifications import WelcomeNotification as BroadcastNotification
from .test_slack_notifications import WelcomeNotification as SlackNotification
from .test_slack_notifications import webhook_url
from .test_vonage_notifications import (
    VonageAPIMock,
    WelcomeNotification as VonageNotification,
)

LoadEnvironment()


class QueueableMailNotification(MailNotification, ShouldQueue):
    def to_mail(self, notifiable):
        return MailComponent().subject("Welcome!")


class QueueableBroadcastNotification(BroadcastNotification, ShouldQueue):
    def to_broadcast(self, notifiable):
        return {"message": "hello"}


class QueueableSlackNotification(SlackNotification, ShouldQueue):
    def to_slack(self, notifiable):
        return SlackComponent().text("Welcome!")


# class QueueableDatabaseNotification(SlackNotification, ShouldQueue):
#     def to_slack(self, notifiable):
#         return SlackComponent().text("Welcome!")


class QueueableVonageNotification(VonageNotification, ShouldQueue):
    def to_slack(self, notifiable):
        return VonageComponent().text("Welcome!").send_from("123456")


class TestQueueingMailNotifications(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.notification = Notification(self.app)
        # configure queueing for tests
        self.app.bind("QueueAsyncDriver", QueueAsyncDriver)
        self.app.bind("Container", self.app)
        self.app.bind("QueueManager", QueueManager(self.app))
        self.app.bind("Queue", QueueManager(self.app).driver("async"))

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_notify_anonymous(self, mock_stderr):
        self.assertIsNone(
            self.notification.route("mail", "test@mail.com").notify(
                QueueableMailNotification()
            )
        )


class TestQueueingBroadcastNotifications(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notification(self.container)
        # configure queueing for tests
        self.container.bind("QueueAsyncDriver", QueueAsyncDriver)
        self.container.bind("Container", self.container)
        self.container.bind("QueueManager", QueueManager(self.container))
        self.container.bind("Queue", QueueManager(self.container).driver("async"))
        self.container.bind("NotificationBroadcastDriver", NotificationBroadcastDriver)
        # tests are made with Pusher driver
        self.container.bind("BroadcastPusherDriver", BroadcastPusherDriver)
        self.container.bind("BroadcastManager", BroadcastManager)

    def test_notify_anonymous(self):
        self.notification.route("broadcast", "users").notify(
            QueueableBroadcastNotification()
        )


class TestQueueingSlackNotifications(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notification(self.container)
        # configure queueing for tests
        self.container.bind("QueueAsyncDriver", QueueAsyncDriver)
        self.container.bind("Container", self.container)
        self.container.bind("QueueManager", QueueManager(self.container))
        self.container.bind("Queue", QueueManager(self.container).driver("async"))

    @responses.activate
    def test_notify_anonymous(self):
        responses.add(responses.POST, webhook_url, body=b"ok")
        self.notification.route("slack", webhook_url).notify(
            QueueableSlackNotification()
        )


class TestQueueingVonageNotifications(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notification(self.container)
        # configure queueing for tests
        # self.container.bind("QueueAsyncDriver", QueueAsyncDriver)
        # self.container.bind("Container", self.container)
        # self.container.bind("QueueManager", QueueManager(self.container))
        # self.container.bind("Queue", QueueManager(self.container).driver("async"))

    def test_notify_anonymous(self):
        with patch("vonage.sms.Sms") as MockSmsClass:
            MockSmsClass.return_value.send_message.return_value = (
                VonageAPIMock().send_success()
            )
            self.notification.route("vonage", "336534231267").notify(
                QueueableVonageNotification()
            )
