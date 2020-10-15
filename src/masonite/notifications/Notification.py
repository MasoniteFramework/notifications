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

    @classmethod
    def notification_type(cls):
        """Get notification type defined with class name."""
        return cls.__name__
