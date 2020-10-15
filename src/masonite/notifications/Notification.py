"""Base Notification facade."""
from abc import ABC, abstractmethod


class Notification(ABC):
    """Base Notification facade."""

    def __init__(self, *args, **kwargs):
        self.id = None
        self._run = True

    def broadcast_on(self):
        """Get the channels the event should broadcast on."""
        return []

    @abstractmethod
    def via(self, notifiable):
        """Defines the notification's delivery channels."""
        return []

    @property
    def should_send(self):
        return self._run

    def dry(self):
        """Sets whether the notification should be sent or not.

        Returns:
            self
        """
        self._run = False
        return self

    @property
    def notification_type(self):
        """Get notification type defined with class name."""
        # TODO: the idea is to get the inherited class, e.g. WelcomeNotification
        # and not Notification
        return self.__name__
