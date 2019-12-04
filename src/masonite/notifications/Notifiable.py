"""Notifiable Class."""

from .components import MailComponent, SlackComponent


class Notifiable(MailComponent, SlackComponent):
    """Notifiable class used as a base class to make a class a notifiable object.

    Arguments:
        MailComponent {notifications.comonents.MailComponent}
        SlackComponent {notifications.comonents.SlackComponent}
    """
    pass
