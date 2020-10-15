from masonite import Mail, Queue
from masonite.app import App
from masonite.drivers import (MailMailgunDriver, MailTerminalDriver,
                              QueueAsyncDriver, BroadcastPusherDriver,
                              BroadcastAblyDriver)
from masonite.managers import QueueManager, BroadcastManager
from masonite.managers.MailManager import MailManager
from masonite.queues import Queueable, ShouldQueue
from masonite.view import View
from src.masonite.notifications import Notifiable, Notify
from masonite.testing import TestCase

from config import queue


class WelcomeNotification(Notifiable):

    template_prefix = '/src/masonite/notifications'
    def mail(self):
        return self.subject('New account signup!') \
            .driver('terminal') \
            .panel('GBALeague.com') \
            .heading('You have created a new account!') \
            .line('We greatly value your service!') \
            .line('Attached is an invoice for your recent purchase') \
            .action('Sign Back In', href="http://gbaleague.com") \
            .line('See you soon! Game on!') \
            .view('/src/masonite/notifications/snippets/mail/heading',
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

    def broadcast(self):
        return self.channel("users").message("new user registered")


class ShouldQueueWelcomeNotification(ShouldQueue, Notifiable):
    template_prefix = '/src/masonite/notifications'

    def mail(self):
        return self.subject('New account signup!') \
            .driver('terminal') \
            .panel('GBALeague.com') \
            .heading('You have created a new account!') \
            .line('We greatly value your service!') \
            .line('Attached is an invoice for your recent purchase') \
            .action('Sign Back In', href="http://gbaleague.com") \
            .line('See you soon! Game on!') \
            .view('/src/masonite/notifications/snippets/mail/heading',
                  {'message': 'Welcome To The GBA!'}) \


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
    DRIVER = 'terminal'

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


class TestNotifiable(TestCase):

    def setUp(self):
        super().setUp()
        self.container.bind('BroadcastPusherDriver', BroadcastPusherDriver)
        self.container.bind('BroadcastAblyDriver', BroadcastAblyDriver)
        self.container.bind('BroadcastManager', BroadcastManager)
        self.notification = WelcomeNotification
        self.notify = Notify(self.container)

    def test_notification_sends_mail(self):
        assert self.notify.mail(WelcomeNotification,
                                to='idmann509@gmail.com') is None

    def test_notification_sends_slack(self):
        assert self.notify.slack(WelcomeNotification) is None

    def test_notification_broadcasting(self):
        assert self.notify.broadcast(WelcomeNotification) is None

    def test_notification_broadcasting_with_channel_override(self):
        assert self.notify.broadcast(WelcomeNotification, channel="other") is None

    def test_notification_broadcasting_with_driver_override(self):
        assert self.notify.broadcast(WelcomeNotification, driver="ably") is None

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

    def test_mail_notification_should_queue(self):
        assert self.notify.mail(ShouldQueueWelcomeNotification,
                                to='test@email.com') is None

    def test_can_send_with_via_method(self):
        notifications = self.notify.via('mail').send(
            ShouldQueueWelcomeNotification, to="test@email.com").called_notifications
        assert isinstance(notifications[0], ShouldQueueWelcomeNotification)

    def test_can_send_with_via_method(self):
        notifications = self.notify.via('mail').send(
            ShouldQueueWelcomeNotification, to="test@email.com").called_notifications
        assert isinstance(notifications[0], ShouldQueueWelcomeNotification)
