""" A NotificationProvider Service Provider """

from masonite.provider import ServiceProvider
from notifications import Notify
from notifications.commands import NotificationCommand


class NotificationProvider(ServiceProvider):

    wsgi = False

    def register(self):
        self.app.bind('Notify', Notify(self.app))
        self.app.bind('NotificationCommand', NotificationCommand())

    def boot(self):
        pass
