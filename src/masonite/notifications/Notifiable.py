"""Notifiable mixin"""
from orator.orm import morph_many
from .Notify import Notify
from .exceptions import NotificationRouteNotImplemented


class Notifiable(object):
    def notify(self, notification, channels=[], dry=False, fail_silently=False):
        """Send the given notification."""
        from wsgi import container

        return Notify(container).send(
            self, notification, channels=[], dry=dry, fail_silently=fail_silently
        )

    def notify_now(self, notification, channels=[], dry=False, fail_silently=False):
        """Send the given notification immediately."""
        from wsgi import container

        return Notify(container).send_now(
            self, notification, channels, dry, fail_silently
        )

    def route_notification_for(self, channel, notification=None):
        """Get the notification routing information for the given channel."""
        # check if routing has been specified on the model
        method_name = "route_notification_for_{0}".format(channel)

        try:
            method = getattr(self, method_name)
            return method(self)
        except AttributeError:
            # if no method is defined on notifiable use default
            if channel == "database":
                # TODO: check how to handle this later
                pass
            elif channel == "mail":
                return self.email
            else:
                raise NotificationRouteNotImplemented(
                    "Notifiable model does not implement {}".format(method_name)
                )

    # TODO: this does not work it returns empty
    # @morph_many('notifiable')
    # def notifications(self):
    #     """Get the entity's notifications. Only for 'database'
    #     notifications."""
    #     from .models import DatabaseNotification
    #     return DatabaseNotification

    def notifications(self):
        """Get the entity's notifications. Only for 'database'
        notifications."""
        from .models import DatabaseNotification

        return (
            DatabaseNotification.where("notifiable_id", self.id)
            .order_by("created_at")
            .get()
        )

    def unread_notifications(self):
        """Get the entity's unread notifications. Only for 'database'
        notifications."""
        return self.notifications().where("read_at", None)

    def read_notifications(self):
        """Get the entity's read notifications. Only for 'database'
        notifications."""
        from .models import DatabaseNotification

        return (
            DatabaseNotification.where("notifiable_id", self.id)
            .where("read_at", "!=", "")
            .order_by("created_at")
            .get()
        )
