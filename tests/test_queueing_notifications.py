import io
import unittest
import unittest.mock
from masonite.drivers import QueueAsyncDriver
from masonite.managers import QueueManager
from masonite.queues import ShouldQueue
from masonite.app import App
from masonite.environment import LoadEnvironment

from src.masonite.notifications import Notification, Notify
from src.masonite.notifications.components import MailComponent

LoadEnvironment()


class MailNotification(Notification, ShouldQueue):
    def to_mail(self, notifiable):
        return MailComponent().subject("Welcome!")

    def via(self, notifiable):
        return ["mail"]


class TestQueueingNotifications(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.notification = Notify(self.app)
        # configure queueing for tests
        self.app.bind("QueueAsyncDriver", QueueAsyncDriver)
        self.app.bind("Container", self.app)
        self.app.bind("QueueManager", QueueManager(self.app))
        self.app.bind("Queue", QueueManager(self.app).driver("async"))

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_with_mail(self, mock_stderr):
        self.assertIsNone(
            self.notification.route("mail", "test@mail.com").notify(MailNotification())
        )
