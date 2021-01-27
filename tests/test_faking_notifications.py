from tests.test_notify import WelcomeNotification
from src.masonite.notifications.Notification import Notification
from tests.UserTestCase import UserTestCase


class TestFakingEntireTestSuite(UserTestCase):

    def setUp(self):
        super().setUp()
        Notification.fake()

    def tearDown(self):
        super().tearDown()
        Notification.restore()

    def test_1(self):
        Notification.assertNothingSent()
        Notification.route("mail", "john.doe@masonite.com").notify(WelcomeNotification("John"))
        Notification.assertSentTo("john.doe@masonite.com", WelcomeNotification)

    def test_2(self):
        Notification.assertNothingSent()
        Notification.route("mail", "john.doe@masonite.com").notify(WelcomeNotification("Joe"))
        Notification.assertSentTo("john.doe@masonite.com", WelcomeNotification,
            lambda notifiable, notif, channels: notif.name == "Joe"
        )
