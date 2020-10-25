from masonite.testing import TestCase

from config.database import Model
from src.masonite.notifications import Notify, Notification, Notifiable
from src.masonite.notifications.components import MailComponent


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ["name", "email", "password"]


class WelcomeNotification(Notification):
    def to_mail(self, notifiable):
        return (
            MailComponent()
            .subject("Welcome {0}".format(notifiable.name))
            .heading("Welcome email heading !")
        )

    def via(self, notifiable):
        return ["mail"]


class UserTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)

    def setUpFactories(self):
        User.create({"name": "Joe", "email": "user@example.com", "password": "secret"})

    def user(self):
        return User.all()[-1]
