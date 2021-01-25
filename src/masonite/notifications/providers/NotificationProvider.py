""" A NotificationProvider Service Provider """
import os
from masonite.provider import ServiceProvider

from .. import Notification
from ..drivers import (
    NotificationMailDriver,
    NotificationBroadcastDriver,
    NotificationDatabaseDriver,
    NotificationSlackDriver,
    NotificationVonageDriver,
)
from ..NotificationManager import NotificationManager
from ..commands import (
    NotificationCommand,
)


class NotificationProvider(ServiceProvider):
    """Notifications Service Provider"""

    wsgi = False

    def register(self):
        self.app.bind("NotificationCommand", NotificationCommand())

        self.app.bind("Notification", Notification(self.app))
        self.app.bind("NotificationMailDriver", NotificationMailDriver)
        self.app.bind("NotificationBroadcastDriver", NotificationBroadcastDriver)
        self.app.bind("NotificationDatabaseDriver", NotificationDatabaseDriver)
        self.app.bind("NotificationSlackDriver", NotificationSlackDriver)
        self.app.bind("NotificationVonageDriver", NotificationVonageDriver)
        self.app.bind("NotificationManager", NotificationManager(self.app))

    def boot(self):
        migration_path = os.path.join(os.path.dirname(__file__), "../migrations")
        config_path = os.path.join(os.path.dirname(__file__), "../config")
        self.publishes(
            {os.path.join(config_path, "notifications.py"): "config/notifications.py"},
            tag="config",
        )
        self.publishes_migrations(
            [
                os.path.join(migration_path, "create_notifications_table.py"),
            ],
        )
