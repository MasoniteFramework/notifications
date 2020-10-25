""" A NotificationProvider Service Provider """

from masonite.provider import ServiceProvider
from .. import Notify
from ..drivers import (
    NotificationMailDriver,
    NotificationBroadcastDriver,
    NotificationDatabaseDriver,
    NotificationSlackDriver,
    NotificationVonageDriver,
)
from ..NotificationManager import NotificationManager
from ..commands import NotificationCommand, NotificationTableCommand


class NotificationProvider(ServiceProvider):
    """Notifications Service Provider"""

    wsgi = False

    def register(self):
        self.app.bind("NotificationCommand", NotificationCommand())
        self.app.bind("NotificationTableCommand", NotificationTableCommand())

        self.app.bind("Notification", Notify(self.app))
        self.app.bind("NotificationMailDriver", NotificationMailDriver)
        self.app.bind("NotificationBroadcastDriver", NotificationBroadcastDriver)
        self.app.bind("NotificationDatabaseDriver", NotificationDatabaseDriver)
        self.app.bind("NotificationSlackDriver", NotificationSlackDriver)
        self.app.bind("NotificationVonageDriver", NotificationVonageDriver)
        self.app.bind("NotificationManager", NotificationManager(self.app))
