""" A NotificationProvider Service Provider """

from masonite.provider import ServiceProvider
from .. import Notify
from ..drivers.NotificationMailDriver import NotificationMailDriver
from ..NotificationManager import NotificationManager
from ..commands import NewNotificationCommand


class NotificationProvider(ServiceProvider):
    """Notifications Service Provider"""
    wsgi = False

    def register(self):
        self.app.bind('Notification', Notify(self.app))
        self.app.bind('NotificationMailDriver', NotificationMailDriver)
        self.app.bind('NotificationManager', NotificationManager(self.app))

        self.app.bind('NewNotificationCommand', NewNotificationCommand())
