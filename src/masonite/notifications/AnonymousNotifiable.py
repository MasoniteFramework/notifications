"""Anonymous Notifiable mixin"""

from .Notifiable import Notifiable


class AnonymousNotifiable(Notifiable):
    """Anonymous notifiable allowing to send notification without having
    a notifiable entity."""

    def __init__(self):
        self._routes = {}

    def route(self, channel, route):
        """Add routing information to the target."""
        if channel == "database":
            return ValueError("The database channel does not support on-demand notifications.")
        self._routes[channel] = route
        return self

    def route_notification_for(self, channel, notification=None):
        try:
            return self._routes[channel]
        except KeyError:
            raise ValueError("Routing has not been defined for the channel {}".format(channel))

    # def notify(self, notification):
    #     """Send the given notification."""
    #     return self.se