"""Notify handler class"""
import uuid
from masonite.app import App
from masonite.queues import ShouldQueue
from config.database import Model

# from .exceptions import InvalidNotificationType


class Notify(object):
    """Notify handler which handle sending/queuing notifications anonymously
    or to notifiables through different channels."""

    called_notifications = []

    def __init__(self, container: App):
        """Notify constructor.

        Arguments:
            container {masonite.app.App} -- Masonite app container.
        """
        self.app = container

    def send(self, notifiables, notification):
        """Send the given notification to the given notifiables."""
        if isinstance(notification, ShouldQueue):
            self.queue_notification(notifiables, notification)
        return self.send_now(notifiables, notification)

    def send_now(self, notifiables, notification, channels=[]):
        """Send the given notification to the given notifiables immediately."""
        notifiables = self.prepare_notifiables(notifiables)
        for notifiable in notifiables:
            # get channels for this notification
            legacy_channels = notification.via(notifiable)
            _channels = legacy_channels if legacy_channels else channels
            for channel in _channels:
                from .AnonymousNotifiable import AnonymousNotifiable
                if isinstance(notifiable, AnonymousNotifiable) and channel == "database":
                    continue
                notification_id = uuid.uuid4()
                self.send_to_notifiable(notifiable, notification, notification_id, channel)

    def send_to_notifiable(self, notifiable, notification, notification_id, channel):
        """Send the given notification through the given channel to one notifiable."""
        if not notification.id:
            notification.id = notification_id
        if not notification.should_send:
            return
        self.app.make("NotificationManager").driver(channel).send(notifiable, notification)

        # TODO: dispatch send event

    def queue_notification(self, notifiables, notification):
        """Queue the given notification."""
        pass

    def prepare_notifiables(self, notifiables):
        from .AnonymousNotifiable import AnonymousNotifiable
        if isinstance(notifiables, Model) or isinstance(notifiables, AnonymousNotifiable):
            return [notifiables]
        else:
            # could be a list or a Collection
            return notifiables

    def route(self, channel, route):
        """Begin sending a notification to an anonymous notifiable."""
        from .AnonymousNotifiable import AnonymousNotifiable
        return AnonymousNotifiable().route(channel, route)
