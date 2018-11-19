from notifications import Notifiable, Notify
from masonite.app import App
from masonite.view import View
from masonite.drivers.MailSmtpDriver import MailSmtpDriver
from masonite.drivers.MailMailgunDriver import MailMailgunDriver
from masonite.managers.MailManager import MailManager
from masonite import Mail


class WelcomeNotification(Notifiable):

    def mail(self):
        return self.subject('New account signup!') \
            .driver('smtp') \
            .panel('GBALeague.com') \
            .heading('You have created a new account!') \
            .line('We greatly value your service!') \
            .line('Attached is an invoice for your recent purchase') \
            .action('Sign Back In', href="http://gbaleague.com") \
            .line('See you soon! Game on!') \
            .view('/notifications/snippets/mail/heading',
                  {'message': 'Welcome To The GBA!'}) \
            .dry()

    def slack(self):
        return self.token('test_token') \
            .dry() \
            .text('Masonite Notification: Read The Docs!, https://docs.masoniteproject.com/') \
            .channel('#bot') \
            .as_user('Masonite Bot') \
            .icon(':fire:') \
            .button('Sure!', "https://docs.masoniteproject.com/") \
            .button('No Thanks!', "http://google.com", style='danger')

class MockMailConfig:
    DRIVER = 'smtp'

    FROM = {
            'address': 'hello@example.com',
            'name': 'Masonite'
        }

    DRIVERS = {
        'smtp': {
            'host': 'smtp.mailtrap.io',
            'port': '465',
            'username': 'username',
            'password': 'password',
        },
    }

class TestNotifiable:

    def setup_method(self):
        self.app = App()
        self.app.bind('Container', self.app)
        self.app.bind('ViewClass', View(self.app))
        # self.app.make('ViewClass').add_environment('notifications/snippets')
        self.app.bind('View', View(self.app).render)
        self.app.bind('MailConfig', MockMailConfig)
        self.app.bind('MailSmtpDriver', MailSmtpDriver)
        self.app.bind('MailMailgunDriver', MailMailgunDriver)
        self.app.bind('MailManager', MailManager(self.app))
        self.app.bind('Mail', self.app.make('MailManager').driver(MockMailConfig.DRIVER))
        self.notification = WelcomeNotification
        self.notify = Notify(self.app)

    def test_notification_sends_mail(self):
        assert self.notify.mail(WelcomeNotification, to='idmann509@gmail.com') is None

    def test_notification_sends_slack(self):
        assert self.notify.slack(WelcomeNotification) is None

    def test_notify_returns_called_notification(self):
        self.notify.mail(WelcomeNotification)
        assert self.notify.called_notifications

    def test_notification_sets_protected_members(self):
        assert self.notify.mail(WelcomeNotification,
                                to='test@email.com') is None
        assert self.notify.called_notifications[0]._to == 'test@email.com'

    def test_mail_notification_appends_template(self):
        assert self.notify.mail(WelcomeNotification,
                                to='test@email.com') is None
        assert 'We greatly value your service!' in self.notify.called_notifications[
            0].template
