import io
import unittest
import unittest.mock
from masonite.testing import TestCase
from masonite.drivers import Mailable

from config.database import Model
from src.masonite.notifications import Notifiable, Notification, Notify
from src.masonite.notifications.components import MailComponent


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ["name", "email", "password"]


class WelcomeEmail(Mailable):
    def __init__(self, name):
        self._name = name

    def build(self):
        return (
            self.subject("Welcome To My Application")
            .reply_to("service@example.com")
            .send_from("admin@example.com")
            .view("notifications/welcome", {"user": self._name})
        )


def to_mail(self, notifiable):
    return WelcomeEmail(notifiable.name).to(notifiable.email)


class WelcomeNotification(Notification):
    def to_mail(self, notifiable):
        return to_mail(self, notifiable)

    def via(self, notifiable):
        return ["mail"]


class CustomNotification(Notification):
    def to_mail(self, notifiable):
        return MailComponent().subject("Welcome!")

    def via(self, notifiable):
        return ["mail"]


class TestMailNotifications(TestCase):
    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        # reset objects to default between tests
        WelcomeNotification.to_mail = to_mail

    def setUpFactories(self):
        User.create({"name": "Joe", "email": "user@example.com", "password": "secret"})

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_notification_should_implements_to_mail(self):
        del WelcomeNotification.to_mail
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual(
            "Notification model should implement to_mail() method.", str(err.exception)
        )

    def test_to_mail_subject(self):
        message = MailComponent().subject("Welcome!")
        self.assertEqual("Welcome!", message._subject)

    def test_to_mail_from(self):
        message = MailComponent().send_from("sam@masonite.com")
        self.assertEqual("sam@masonite.com", message._from)

        message = MailComponent().send_from("sam@masonite.com", "Sam from Masonite")
        self.assertTupleEqual(("sam@masonite.com", "Sam from Masonite"), message._from)

    def test_to_mail_line(self):
        message = MailComponent().line("Welcome line!")
        self.assertIn("Welcome line!", message.template)
        self.assertIn("</p>", message.template)

    def test_to_mail_heading(self):
        message = MailComponent().heading("Welcome heading!")
        self.assertIn("Welcome heading!", message.template)

    def test_to_mail_action(self):
        message = MailComponent().action("Connect", href="/login")
        self.assertIn("Connect", message.template)
        self.assertIn('href="/login"', message.template)
        self.assertIn('class="btn"', message.template)
        self.assertIn("</button>", message.template)

        message = MailComponent().action("Connect", href="/login", style="primary")
        self.assertIn('class="btn btn-primary"', message.template)

    def test_to_mail_action_with_level(self):
        message = MailComponent().error().action("Connect", href="/login")
        self.assertIn('class="btn btn-error"', message.template)

        message = MailComponent().success().action("Connect", href="/login")
        self.assertIn('class="btn btn-success"', message.template)

    def test_to_mail_panel(self):
        message = MailComponent().panel("Welcome panel!")
        self.assertIn("Welcome panel!", message.template)
        self.assertIn("</div>", message.template)

    def test_to_mail_with_components(self):
        message = (
            MailComponent()
            .subject("Welcome!")
            .heading("Welcome here!")
            .line("You registered here.")
            .action("Confirm your email", href="/login")
            .line("Best regards")
        )

        self.assertIn("Welcome!", message._subject)
        self.assertIn("Welcome here!", message.template)
        self.assertIn("You registered here.", message.template)
        self.assertIn("Confirm your email", message.template)
        self.assertIn("Best regards", message.template)

    def test_to_mail_with_view(self):
        message = MailComponent().view("notifications.welcome", {"user": "Sam"})
        self.assertIn("Welcome Sam!", message.template)

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_with_send_from(self, mock_stderr):
        user = self.user()

        def to_mail(self, notifiable):
            return MailComponent().send_from("noreply@masonite.com")

        CustomNotification.to_mail = to_mail
        user.notify(CustomNotification())
        # When no name is defined, Masonite is added to address
        self.assertIn('From: "Masonite" <noreply@masonite.com>', mock_stderr.getvalue())

        def to_mail(self, notifiable):
            return MailComponent().send_from("noreply@masonite.com", "No-Reply")

        CustomNotification.to_mail = to_mail
        user.notify(CustomNotification())
        self.assertIn('From: "No-Reply" <noreply@masonite.com>', mock_stderr.getvalue())

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_with_reply_to(self, mock_stderr):
        user = self.user()

        def to_mail(self, notifiable):
            return MailComponent().reply_to("support@masonite.com")

        CustomNotification.to_mail = to_mail
        user.notify(CustomNotification())
        self.assertIn("Reply-To: ['support@masonite.com']", mock_stderr.getvalue())

        # TODO: not possible for now in Masonite:
        # Mail driver does not support naming reply-to addresses
        # def to_mail(self, notifiable):
        #     return MailComponent().reply_to("support@masonite.com", "Masonite Support")
        # CustomNotification.to_mail = to_mail
        # user.notify(CustomNotification())
        # self.assertIn('Reply-To: "Masonite Support" <support@masonite.com>', mock_stderr.getvalue())

        def to_mail(self, notifiable):
            return MailComponent().reply_to(["joe@masonite.com", "john@masonite.com"])

        CustomNotification.to_mail = to_mail
        user.notify(CustomNotification())
        self.assertIn(
            "Reply-To: ['joe@masonite.com', 'john@masonite.com']",
            mock_stderr.getvalue(),
        )

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_with_components(self, mock_stderr):
        user = self.user()

        def to_mail(self, notifiable):
            return (
                MailComponent()
                .subject("Welcome!")
                .heading("Welcome here!")
                .send_from("noreply@masonite.com")
            )

        CustomNotification.to_mail = to_mail

        user.notify(CustomNotification())
        printed_email = mock_stderr.getvalue()
        # When no name is defined, Masonite is added to address
        self.assertIn('From: "Masonite" <noreply@masonite.com>', printed_email)
        self.assertIn("Subject: Welcome!", printed_email)
        self.assertIn("Welcome here!", printed_email)

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_with_mailable(self, mock_stderr):
        user = self.user()
        user.notify(WelcomeNotification())
        printed_email = mock_stderr.getvalue()
        self.assertIn("Welcome To My Application", printed_email)
        self.assertIn("user@example.com", printed_email)
        self.assertIn("Welcome Joe", printed_email)

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_to_anonymous(self, mock_stderr):
        self.notification.route("mail", "test@mail.com").notify(CustomNotification())
        self.assertIn("To: test@mail.com", mock_stderr.getvalue())
        self.assertIn("Welcome!", mock_stderr.getvalue())
