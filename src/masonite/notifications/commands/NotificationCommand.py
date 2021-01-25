"""Notification Command."""
from masonite.commands import BaseScaffoldCommand


class NotificationCommand(BaseScaffoldCommand):
    """
    Creates a new Notification class.

    notification
        {name : Name of the Notification class you want to create}
    """

    scaffold_name = "Notification"
    base_directory = "app/notifications/"
    template = "/masonite/notifications/snippets/scaffold/notification"
    postfix = "Notification"
