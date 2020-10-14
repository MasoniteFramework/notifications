from abc import abstractmethod
from abc import ABC as Contract


class NotificationContract(Contract):
    """Abstract Channel class to define new notification channels."""

    @abstractmethod
    def send(self, notifiable, notification):
        """Implements sending the notification to notifiables through
        this channel."""
        raise NotImplementedError("send() method must be implemented for a notification channel.")
