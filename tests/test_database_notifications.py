import io
import unittest
import unittest.mock
import uuid
from masonite.testing import TestCase
from masoniteorm.models import Model
from masoniteorm.factories import Factory

# from app.User import User
from src.masonite.notifications import (
    Notifiable,
    Notification,
    Notify,
    DatabaseNotification,
)
from src.masonite.notifications.drivers import NotificationDatabaseDriver
import pendulum


# class UserTest(User, Notifiable):
#     """Notifiable User Test Model"""

#     __table__ = "users"

class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ["name", "email", "password"]

    def route_notification_for_slack(self, notifiable):
        return "#channel-{}".format(self.name.lower())


def to_database(self, notifiable):
    return {"data": "Welcome {0}!".format(notifiable.name)}


class WelcomeNotification(Notification):
    def to_database(self, notifiable):
        return to_database(self, notifiable)

    def via(self, notifiable):
        return ["database"]


notification_data = {
    "id": str(uuid.uuid4()),
    "read_at": None,
    "type": "TestNotification",
    "data": "test",
    "notifiable_id": 1,
    "notifiable_type": "users"
}


class TestDatabaseNotifications(TestCase):
    sqlite = False

    def setUp(self):
        super().setUp()
        self.notification = Notify(self.container)
        self.container.bind("NotificationDatabaseDriver", NotificationDatabaseDriver)
        self.database_driver = self.container.make("NotificationDatabaseDriver")
        # reset objects to default between tests
        WelcomeNotification.to_database = to_database
        for n in DatabaseNotification.all():
            n.delete()

    def setUpFactories(self):
        User.create(
            {"name": "Joe", "email": "user@example.com", "password": "secret"}
        )

    def user(self):
        return User.where("name", "Joe").get()[0]

    def test_sending_notification_to_user(self):
        user = self.user()
        user.notify(WelcomeNotification())
        self.assertEqual(1, DatabaseNotification.count())

    def test_database_driver_get_data(self):
        user = self.user()
        data = self.database_driver.get_data("database", user, WelcomeNotification())
        self.assertDictEqual({"data": "Welcome Joe!"}, data)

    def test_database_driver_build_payload(self):
        user = self.user()
        notification = WelcomeNotification()
        payload = self.database_driver.build_payload(user, notification)
        self.assertDictEqual(
            {
                "id": str(notification.id),
                "type": "WelcomeNotification",
                "notifiable_id": user.id,
                "notifiable_type": "users",
                "data": '{"data": "Welcome Joe!"}',
                "read_at": None,
            },
            payload,
        )

    def test_notification_should_implements_to_database(self):
        del WelcomeNotification.to_database
        user = self.user()
        with self.assertRaises(NotImplementedError) as err:
            user.notify(WelcomeNotification())
        self.assertEqual(
            "Notification model should implement to_database() method.",
            str(err.exception),
        )

    def test_database_notification_morph_notifiable(self):
        class UserNotifiableTest(User, Notifiable):
            """Notifiable User Test Model"""

            __table__ = "users"

        user = UserNotifiableTest.where("name", "Joe").get()[0]
        notification = DatabaseNotification.create(
            {
                **notification_data,
                "read_at": pendulum.now().to_datetime_string(),
                "notifiable_id": user.id,
            }
        )
        self.assertEqual(user.id, notification.notifiable_id)
        self.assertEqual(UserNotifiableTest.get_table_name(), notification.notifiable_type)

    def test_database_notification_read_state(self):
        notification = DatabaseNotification.create({
            **notification_data,
            "read_at": pendulum.now().to_datetime_string(),
        })
        self.assertTrue(notification.is_read)
        notification.read_at = None
        self.assertFalse(notification.is_read)

    def test_database_notification_unread_state(self):
        notification = DatabaseNotification.create({
            **notification_data,
            "read_at": pendulum.now().to_datetime_string(),
        })
        self.assertFalse(notification.is_unread)
        notification.read_at = None
        self.assertTrue(notification.is_unread)

    def test_database_notification_mark_as_read(self):
        notification = DatabaseNotification.create(notification_data)
        notification.mark_as_read()
        self.assertNotEqual(None, notification.read_at)

    def test_database_notification_mark_as_unread(self):
        notification = DatabaseNotification.create({
            **notification_data,
            "read_at": pendulum.now().to_datetime_string(),
        })
        notification.mark_as_unread()
        self.assertEqual(None, notification.read_at)

    def test_notifiable_get_notifications(self):
        user = self.user()
        self.assertEqual(0, user.notifications.count())
        user.notify(WelcomeNotification())
        self.assertEqual(1, user.notifications.count())

    def test_notifiable_get_read_notifications(self):
        user = self.user()
        self.assertEqual(0, user.read_notifications.count())
        DatabaseNotification.create(
            {
                **notification_data,
                "read_at": pendulum.yesterday().to_datetime_string(),
                "notifiable_id": user.id,
            }
        )
        self.assertEqual(1, user.read_notifications.count())

    def test_notifiable_get_unread_notifications(self):
        user = self.user()
        self.assertEqual(0, user.unread_notifications.count())
        DatabaseNotification.create(
            {
                **notification_data,
                "notifiable_id": user.id,
            }
        )
        self.assertEqual(1, user.unread_notifications.count())

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_sending_to_anonymous_not_possible(self, mock_stderr):
        with self.assertRaises(ValueError):
            self.notification.route("database", "test@mail.com").notify(
                WelcomeNotification()
            )
