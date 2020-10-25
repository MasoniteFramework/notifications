from abc import abstractmethod
from abc import ABC as Contract


class NotificationContract(Contract):
    """Abstract Channel class to define new notification channels."""

    @abstractmethod
    def send(self, notifiable, notification):
        """Implements sending the notification to notifiables through
        this channel."""
        raise NotImplementedError(
            "send() method must be implemented for a notification channel."
        )

    def get_data(self, channel, notifiable, notification):
        """Get the data for the notification."""
        method_name = "to_{0}".format(channel)
        try:
            method = getattr(notification, method_name)
            return method(notifiable)
        except AttributeError:
            raise NotImplementedError(
                "Notification model should implement {}() method.".format(method_name)
            )
