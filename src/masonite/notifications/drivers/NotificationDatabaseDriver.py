"""Database driver Class."""
import json
from masonite.app import App
from masonite import Queue, Broadcast
from masonite.helpers import config
from masonite.queues import ShouldQueue
from masonite.drivers import BaseDriver
from masoniteorm.relationships import morph_to
from ..NotificationContract import NotificationContract
from ..models import DatabaseNotification


class NotificationDatabaseDriver(BaseDriver, NotificationContract):
    def __init__(self, app: App):
        """Database Driver Constructor."""
        self.app = app

    def send(self, notifiable, notification):
        """Used to send the email and run the logic for sending emails."""
        model_data = self.build_payload(notifiable, notification)
        return DatabaseNotification.create(model_data)

    def queue(self, notifiable, notification):
        """Used to queue the database notification creation."""
        # TODO:
        pass

    def serialize_data(self, data):
        return json.dumps(data)

    def build_payload(self, notifiable, notification):
        """Build an array payload for the DatabaseNotification Model."""
        # TODO: if notifiable is not instance of Model it won't work ...
        # TODO: if notifiable PK is not integer it won't work ...
        return {
            "id": str(notification.id),
            "type": notification.notification_type(),
            "notifiable_id": notifiable.id,
            "notifiable_type": notifiable.get_table_name(),
            "data": self.serialize_data(
                self.get_data("database", notifiable, notification)
            ),
            "read_at": None,
        }
