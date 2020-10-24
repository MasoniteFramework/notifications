import io
import sys
import unittest
import unittest.mock
from masonite.testing import TestCase

from src.masonite.notifications import Notification, Notify
from src.masonite.notifications.components import MailComponent


class WelcomeNotification(Notification):

    def to_mail(self, notifiable):
        return MailComponent().subject('Welcome')

    def via(self, notifiable):
        return ["mail"]


class TestNotificationClass(TestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)

    def test_should_send(self):
        notification = WelcomeNotification()
        self.assertTrue(notification.should_send)
        notification.dry()
        self.assertFalse(notification.should_send)

    def test_ignore_errors(self):
        notification = WelcomeNotification()
        self.assertFalse(notification.ignore_errors)
        notification.fail_silently()
        self.assertTrue(notification.ignore_errors)

    def test_notification_type(self):
        self.assertEqual("WelcomeNotification",
                         WelcomeNotification().notification_type())
