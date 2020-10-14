"""Broadcast Component Class."""

from masonite import Queue, Broadcast
from masonite.helpers import config
from masonite.queues import ShouldQueue
from ..exceptions import InvalidNotificationType


class BroadcastComponent:
    _driver = None
    _run = True
    _channel = ""
    _message = ""

    def __init__(self, app):
        """Broadcast Component Constructor."""
        self.app = app
        self._driver = None
        self._channel = None

    def message(self, message):
        """Specifies the message to be broadcasted to the channel.

        Arguments:
            message {string} -- The text to show in the message.

        Returns:
            self
        """
        self._message = message
        return self

    def channel(self, channel):
        """Specifies the channel to broadcast to.

        Arguments:
            channel {string} -- The channel to broadcast to.

        Returns:
            self
        """
        self._channel = channel
        return self

    def driver(self, driver):
        """Specifies the driver to use.

        Arguments:
            driver {string} -- The name of the driver.

        Returns:
            self
        """
        self._driver = driver
        return self

    def broadcast(self):
        """Used to show a not implemented type exception.

        Raises:
            Exception
        """
        raise Exception(
            'The {} notification does not have a broadcast method'.format(self))

    def fire_broadcast(self, channel=None, driver=None):
        """Used to fire the actual message and run the logic for broadcasting messages.
        """
        # select driver to use
        _driver = None
        if driver:
            _driver = driver
        elif self._driver:
            _driver = self._driver
        else:
            _driver = config('broadcast.driver')
        # select channel to use
        if channel:
            _channel = channel
        else:
            _channel = self._channel
        broadcast = self.app.make('BroadcastManager').driver(_driver)
        if self._run:
            if isinstance(self, ShouldQueue):
                self.app.make(Queue).push(broadcast.channel, args=(_channel, self._message))
            else:
                broadcast.channel(_channel, self._message)
