from masonite.testing import TestCase
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


class TestNotifiable(TestCase):

    def setUp(self):
        super().setUp()
        self.notify = Notify(self.container)

    def setUpFactories(self):
        User.create({
            'name': 'Joe',
            'email': 'user@example.com',
            'password': 'secret'
        })

    def test_user_as_notifiable_entity(self):
        user = User.find(1)
        self.assertEqual([], user.notifications())
        self.assertEqual([], user.read_notifications())
        self.assertEqual([], user.unread_notifications())
        self.assertTrue(callable(user.notify))
        self.assertTrue(callable(user.notify_now))

    def test_send_notification_to_user(self):
        user = User.find(1)
        user.notify(WelcomeNotification())