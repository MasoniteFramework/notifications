"""Channel Manager module."""
from masonite.managers import Manager


class NotificationManager(Manager):
    """Manages all notifications drivers.

    Arguments:
        Manager {from .managers.Manager} -- The base Manager class.
    """

    config = None
    driver_prefix = "Notification"
