import io
import unittest
import unittest.mock
from masonite.testing import TestCase
from masonite.drivers import Mailable, BroadcastPusherDriver
from masonite.managers import BroadcastManager

from config.database import Model
from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.drivers import NotificationBroadcastDriver


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ['name', 'email', 'password']


def to_broadcast(self, notifiable):
    return {
        "data": "Welcome {0}!".format(notifiable.name)
    }


class WelcomeNotification(Notification):

    def to_broadcast(self, notifiable):
        return to_broadcast(self, notifiable)

    def via(self, notifiable):
        return ["broadcast"]


class TestBroadcastNotifications(TestCase):

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        self.container.bind('NotificationBroadcastDriver', NotificationBroadcastDriver)
        # tests are made with Pusher driver
        self.container.bind('BroadcastPusherDriver', BroadcastPusherDriver)
        self.container.bind('BroadcastManager', BroadcastManager)

        self.broadcast_driver = self.container.make('NotificationBroadcastDriver')
        # reset objects to default between tests
        WelcomeNotification.broadcast_on = lambda self: []
        WelcomeNotification.to_broadcast = to_broadcast
        User.receives_broadcast_notifications_on = None

    def setUpFactories(self):
        User.create({
            'name': 'Joe',
            'email': 'user@example.com',
            'password': 'secret'
        })

    def user(self):
        return User.all()[-1]

    def test_sending_notification_to_user(self):
        def broadcast_on(self):
            return "all_users"
        WelcomeNotification.broadcast_on = broadcast_on
        user = self.user()
        user.notify(WelcomeNotification())

    def test_should_define_receives_broadcast_notifications_on(self):
        """When broadcast_on not defined on notification class, this method
        should be defined on Notifiable."""
        user = self.user()
        with self.assertRaises(NotImplementedError):
            user.notify(WelcomeNotification())

    def test_receives_broadcast_notifications_on(self):
        # add method to notifiable
        def receives_broadcast_notifications_on(notifiable):
            return "users.{}".format(notifiable.id)
        User.receives_broadcast_notifications_on = receives_broadcast_notifications_on
        user = self.user()
        user.notify(WelcomeNotification())

    def test_broadcast_driver_channels_are_set(self):
        User.receives_broadcast_notifications_on = lambda self: "channel_1"
        user = self.user()
        channels = self.broadcast_driver.broadcast_on(user, WelcomeNotification())
        self.assertEqual(["channel_1"], channels)

        User.receives_broadcast_notifications_on = None
        WelcomeNotification.broadcast_on = lambda self: "channel_1"
        channels = self.broadcast_driver.broadcast_on(user, WelcomeNotification())
        self.assertEqual(["channel_1"], channels)

        WelcomeNotification.broadcast_on = lambda self: ["channel_1", "channel_2"]
        channels = self.broadcast_driver.broadcast_on(user, WelcomeNotification())
        self.assertEqual(["channel_1", "channel_2"], channels)

    def test_broadcast_driver_get_data(self):
        user = self.user()
        WelcomeNotification.to_broadcast = lambda self, notifiable: {"message": "hello"}
        data = self.broadcast_driver.get_data("broadcast", user, WelcomeNotification())
        self.assertDictEqual({"message": "hello"}, data)

        WelcomeNotification.to_broadcast = lambda self, notifiable: {"message": "hello {0}".format(notifiable.name)}
        data = self.broadcast_driver.get_data("broadcast", user, WelcomeNotification())
        self.assertDictEqual({"message": "hello Joe"}, data)

    def test_notification_should_implements_to_broadcast(self):
        del WelcomeNotification.to_broadcast
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual("Notification model should implement to_broadcast() method.",
                         str(err.exception))

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_sending_to_anonymous(self, mock_stderr):
        WelcomeNotification.to_broadcast = lambda self, notifiable: {"message": "hello"}
        self.notification.route("broadcast", "users").notify(WelcomeNotification())