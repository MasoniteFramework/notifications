"""Notification handler class"""
import uuid
from masonite.app import App
from masonite.exceptions import DriverNotFound
from masonite.queues import ShouldQueue
from masoniteorm.models import Model

from .NotificationContract import NotificationContract
from .exceptions import InvalidNotificationType, NotificationChannelsNotDefined
from .Mockable import MockableService


class Notification(MockableService):
    """Notification handler which handle sending/queuing notifications anonymously
    or to notifiables through different channels."""

    __service__ = "Notification"

    @classmethod
    def get_mock_class(cls):
        from .NotificationTester import NotificationTester
        return NotificationTester

    def __init__(self, container: App):
        """Notification constructor.

        Arguments:
            container {masonite.app.App} -- Masonite app container.
        """
        self.app = container

    def send(
        self, notifiables, notification, channels=[], dry=False, fail_silently=False
    ):
        """Send the given notification to the given notifiables immediately."""
        notifiables = self.prepare_notifiables(notifiables)
        for notifiable in notifiables:
            # get channels for this notification
            # allow override of channels list at send
            _channels = channels if channels else notification.via(notifiable)
            _channels = self.prepare_channels(_channels)
            if not _channels:
                raise NotificationChannelsNotDefined(
                    "No channels have been defined in via() method of {0} class.".format(
                        notification.notification_type()
                    )
                )
            for channel in _channels:
                from .AnonymousNotifiable import AnonymousNotifiable

                if (
                    isinstance(notifiable, AnonymousNotifiable)
                    and channel == "database"
                ):
                    continue
                notification_id = uuid.uuid4()
                self.send_or_queue(
                    notifiable,
                    notification,
                    notification_id,
                    channel,
                    dry=dry,
                    fail_silently=fail_silently,
                )

    def is_custom_channel(self, channel):
        return issubclass(channel, NotificationContract)

    def send_or_queue(
        self,
        notifiable,
        notification,
        notification_id,
        channel_instance,
        dry=False,
        fail_silently=False,
    ):
        """Send or queue the given notification through the given channel to one notifiable."""
        if not notification.id:
            notification.id = notification_id
        if not notification.should_send or dry:
            return
        try:
            if isinstance(notification, ShouldQueue):
                return channel_instance.queue(notifiable, notification)
            else:
                return channel_instance.send(notifiable, notification)
        except Exception as e:
            if notification.ignore_errors or fail_silently:
                pass
            else:
                raise e

        # TODO (later): dispatch send event

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

    # def route(self, channel, route):
    #     """Begin sending a notification to an anonymous notifiable."""
    #     from .AnonymousNotifiable import AnonymousNotifiable

    #     return AnonymousNotifiable().route(channel, route)
    @staticmethod
    def route(channel, route):
        """Begin sending a notification to an anonymous notifiable."""
        from .AnonymousNotifiable import AnonymousNotifiable

        return AnonymousNotifiable().route(channel, route)

    # @classmethod
    # def fake(cls):
    #     from .NotificationTester import NotificationTester
    #     from wsgi import container

    #     tester = NotificationTester(container)
    #     container.bind("Notification", tester)
    #     return tester

    # @classmethod
    # def restore(cls):
    #     from wsgi import container

    #     return container.bind("Notification", cls(container))
