"""Notification Table Command."""
import os
from cleo import Command


class NotificationTableCommand(Command):
    """
    Creates the migration for the table 'notifications' used by the
    database notification driver.

    notification:table
    """

    def handle(self):
        migration_path = os.path.join(os.path.dirname(__file__), "../migrations")
        self.publishes_migrations(
            [
                os.path.join(migration_path, "create_notifications_table.py"),
            ]
        )
