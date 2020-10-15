import io
import unittest
import unittest.mock

from .UserTestCase import UserTestCase
from src.masonite.notifications import Notification
from src.masonite.notifications.components.MailComponent import MailComponent


class WelcomeNotification(Notification):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def to_mail(self, notifiable):
        return MailComponent().subject('Welcome {0}!'.format(self.name)).heading('Welcome email heading !')

    def via(self, notifiable):
        return ["mail"]


class TestNotifyHandler(UserTestCase):

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user(self, mock_stderr):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).notify(WelcomeNotification("John"))
        printed_email = mock_stderr.getvalue()
        self.assertIn('john.doe@masonite.com', printed_email)
        self.assertIn('Welcome John', printed_email)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_send_notification_to_anonymous_user_with_multiple_channels(self, mock_stderr):
        user_email = "john.doe@masonite.com"
        self.notification.route("mail", user_email).route("slack", "#general").notify(WelcomeNotification("John"))
        # check email notification sent
        printed_email = mock_stderr.getvalue()
        self.assertIn('john.doe@masonite.com', printed_email)
        # TODO: check Slack notification sent ?
