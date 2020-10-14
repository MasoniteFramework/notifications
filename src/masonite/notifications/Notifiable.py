"""Notifiable Class."""

from .components import MailComponent, SlackComponent, BroadcastComponent


class Notifiable(MailComponent, SlackComponent, BroadcastComponent):
    """Notifiable class used as a base class to make a class a notifiable object.

    Arguments:
        MailComponent {notifications.components.MailComponent}
        SlackComponent {notifications.components.SlackComponent}
        BroadcastComponent {notifications.components.BroadcastComponent}
    """
    pass
