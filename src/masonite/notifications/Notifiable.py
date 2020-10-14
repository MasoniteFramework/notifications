"""Notifiable mixin"""
from .Notify import Notify


class Notifiable(object):

    def notify(self, notification):
        """Send the given notification."""
        from wsgi import container
        Notify(container).send(self, notification)

    def notify_now(self, notification, channels=[]):
        """Send the given notification immediately."""
        from wsgi import container
        Notify(container).send_now(self, notification, channels)

    def route_notification_for(self, channel, notification=None):
        """Get the notification routing information for the given channel."""
        # check if routing has been specified on the model
        method_name = "route_notification_for_{0}".format(channel)

        try:
            method = getattr(self, method_name)
            return method(notification)
        except AttributeError:
            if channel == "database":
                # TODO: check how to handle this later
                pass
            elif channel == "mail":
                return self.email
            else:
                raise Exception("Notifiable model does not implement {}".format(method_name))

    def notifications(self):
        """Get the entity's notifications."""
        return []

    def unread_notifications(self):
        """Get the entity's unread notifications."""
        # TODO: self.notifications().where('read_at', '!=', None)
        return []

    def read_notifications(self):
        """Get the entity's read notifications."""
        # TODO: self.notifications().where('read_at', None)
        return []
