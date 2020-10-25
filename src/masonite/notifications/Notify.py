"""Notify handler class"""
import uuid
from masonite.app import App
from masonite.exceptions import DriverNotFound
from masonite.queues import ShouldQueue
from config.database import Model

from .NotificationContract import NotificationContract
from .exceptions import InvalidNotificationType


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

    def is_custom_channel(self, channel):
        return issubclass(channel, NotificationContract)

    def send_to_notifiable(
        self,
        notifiable,
        notification,
        notification_id,
        channel_instance,
        dry=False,
        fail_silently=False,
    ):
        """Send the given notification through the given channel to one notifiable."""
        if not notification.id:
            notification.id = notification_id
        if not notification.should_send or dry:
            return
        try:
            channel_instance.send(notifiable, notification)
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
        """Check channels list to get a list of channels string name which
        will be fetched from container later and also checks if custom notifications
        classes are provided.

        For custom notifications check that the class implements NotificationContract.
        For driver notifications (official or not) check that the driver exists in the container.
        """
        _channels = []
        for channel in channels:
            if isinstance(channel, str):
                # check that related notification driver is known and registered in the container
                try:
                    _channels.append(
                        self.app.make("NotificationManager").driver(channel)
                    )
                except DriverNotFound:
                    raise InvalidNotificationType(
                        "{0} notification driver has not been found in the container. Check that it is registered correctly.".format(
                            channel
                        )
                    )
            elif self.is_custom_channel(channel):
                _channels.append(channel())
            else:
                raise InvalidNotificationType(
                    "{0} notification class cannot be used because it does not implements NotificationContract.".format(
                        channel
                    )
                )

        return _channels

    def route(self, channel, route):
        """Begin sending a notification to an anonymous notifiable."""
        from .AnonymousNotifiable import AnonymousNotifiable

        return AnonymousNotifiable().route(channel, route)
