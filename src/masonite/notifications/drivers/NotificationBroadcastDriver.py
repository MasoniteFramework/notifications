"""Broadcast driver Class."""
from masonite.app import App
from masonite import Queue, Broadcast
from masonite.helpers import config
from masonite.queues import ShouldQueue
from masonite.drivers import BaseDriver

from ..NotificationContract import NotificationContract
from ..exceptions import BroadcastOnNotImplemented


class NotificationBroadcastDriver(BaseDriver, NotificationContract):
    _driver = None

    def __init__(self, app: App):
        """Broadcast Driver Constructor."""
        self.app = app
        self._driver = None

    def driver(self, driver):
        """Specifies the driver to use.

        Arguments:
            driver {string} -- The name of the driver.

        Returns:
            self
        """
        self._driver = driver
        return self

    def send(self, notifiable, notification):
        """Used to send the email and run the logic for sending emails."""
        data = self.get_data("broadcast", notifiable, notification)
        driver_instance = self.get_broadcast_driver()
        channels = self.broadcast_on(notifiable, notification)
        for channel in channels:
            driver_instance.channel(channel, data)

    def get_broadcast_driver(self):
        """Shortcut method to get given broadcast driver instance."""
        driver = config("broadcast.driver") if not self._driver else None
        return self.app.make("BroadcastManager").driver(driver)

    def broadcast_on(self, notifiable, notification):
        """Get the channels the notification should be broadcasted on."""
        channels = notification.broadcast_on()
        if not channels:
            from ..AnonymousNotifiable import AnonymousNotifiable

            if isinstance(notifiable, AnonymousNotifiable):
                channels = notifiable.route_notification_for("broadcast", notification)
            else:
                try:
                    channels = notifiable.receives_broadcast_notifications_on()
                except AttributeError:
                    raise BroadcastOnNotImplemented(
                        """No broadcast channels defined for the Notification with broadcast_on(),
                    receives_broadcast_notifications_on() must be defined on the Notifiable."""
                    )

        if isinstance(channels, str):
            channels = [channels]
        return channels
