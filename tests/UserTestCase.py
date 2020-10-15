from masonite.testing import TestCase

from app.User import User
from src.masonite.notifications import Notify, Notification
from src.masonite.notifications.components import MailComponent


class WelcomeNotification(Notification):

    def to_mail(self, notifiable):
        return MailComponent().subject('Welcome {0}'.format(notifiable.name)).heading('Welcome email heading !')

    def via(self, notifiable):
        return ["mail"]


class UserTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)

    def setUpFactories(self):
        User.create({
            'name': 'Joe',
            'email': 'user@example.com',
            'password': 'secret'
        })

    def user(self):
        return User.find(1)
