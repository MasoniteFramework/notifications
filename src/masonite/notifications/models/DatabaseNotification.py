"""DatabaseNotification Model."""
from orator.orm import morph_to
from config.database import Model
import pendulum


class DatabaseNotification(Model):
    """DatabaseNotification Model."""
    __fillable__ = ['id', 'type', 'data', 'read_at', 'notifiable_id', 'notifiable_type']
    __table__ = "notifications"

    @morph_to
    def notifiable(self):
        """Get the notifiable entity that the notification belongs to."""
        return

    def mark_as_read(self):
        """Mark the notification as read."""
        if not self.read_at:
            self.set_raw_attribute('read_at', pendulum.now())

    def mark_as_unread(self):
        """Mark the notification as unread."""
        if self.read_at:
            self.set_raw_attribute('read_at', None)

    @property
    def is_read(self):
        """Determine if a notification has been read."""
        return self.read_at is not None

    @property
    def is_unread(self):
        """Determine if a notification has not been read yet."""
        return self.read_at is None
