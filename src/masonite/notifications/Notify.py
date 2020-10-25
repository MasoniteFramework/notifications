"""Notify handler class"""
import uuid
from masonite.app import App
from masonite.queues import ShouldQueue
from masonite.drivers import BaseDriver
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

    def send(
        self, notifiables, notification, channels=[], dry=False, fail_silently=False
    ):
        """Send the given notification to the given notifiables."""
        if isinstance(notification, ShouldQueue):
            self.queue_notification(notifiables, notification)
        return self.send_now(
            notifiables, notification, dry=dry, fail_silently=fail_silently
        )

    def send_now(
        self, notifiables, notification, channels=[], dry=False, fail_silently=False
    ):
        """Send the given notification to the given notifiables immediately."""
        notifiables = self.prepare_notifiables(notifiables)
        for notifiable in notifiables:
            # get channels for this notification
            legacy_channels = notification.via(notifiable)
            _channels = legacy_channels if legacy_channels else channels
            # TODO: prepare channels check only strings or channel driver class
            _channels = self.prepare_channels(_channels)
            for channel in _channels:
                from .AnonymousNotifiable import AnonymousNotifiable

                if (
                    isinstance(notifiable, AnonymousNotifiable)
                    and channel == "database"
                ):
                    continue
                notification_id = uuid.uuid4()
                self.send_to_notifiable(
                    notifiable,
                    notification,
                    notification_id,
                    channel,
                    dry=dry,
                    fail_silently=fail_silently,
                )

    def send_to_notifiable(
        self,
        notifiable,
        notification,
        notification_id,
        channel,
        dry=False,
        fail_silently=False,
    ):
        """Send the given notification through the given channel to one notifiable."""
        if not notification.id:
            notification.id = notification_id
        if not notification.should_send or dry:
            return
        try:
            self.app.make("NotificationManager").driver(channel).send(
                notifiable, notification
            )
        # TODO: should we subclass exception which can occur during sending with NotificationSendingException ?
        # could allow to catch only those ones
        except Exception as e:
            if notification.ignore_errors or fail_silently:
                pass
            else:
                raise e

        # TODO: dispatch send event

    def queue_notification(self, notifiables, notification):
        """Queue the given notification."""
        pass

    def prepare_notifiables(self, notifiables):
        from .AnonymousNotifiable import AnonymousNotifiable

        if isinstance(notifiables, Model) or isinstance(
            notifiables, AnonymousNotifiable
        ):
            return [notifiables]
        else:
            # could be a list or a Collection
            return notifiables

    def prepare_channels(self, channels):
        """Process channels list to get a list of channels name. The list can
        indeed contain channels class."""
        _channels = []
        for channel in channels:
            if isinstance(channel, str):
                _channels.append(channel)
            # check base driver class else discard OR raise exception ?
            elif issubclass(channel, BaseDriver):
                # get channel name
                name = channel.replace("Driver", "").lower()
                # TODO: from this name can we import driver if not registered in IOC ? No !
                # We should instead get an import path ..
                _channels.append(name)
        return _channels

    def route(self, channel, route):
        """Begin sending a notification to an anonymous notifiable."""
        from .AnonymousNotifiable import AnonymousNotifiable

        return AnonymousNotifiable().route(channel, route)
