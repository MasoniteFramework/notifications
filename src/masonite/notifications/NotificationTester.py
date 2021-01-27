from functools import reduce
import collections


from .Notification import Notification
from .Notifiable import Notifiable
from .AnonymousNotifiable import AnonymousNotifiable


def deep_get(dictionary, keys, default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)


def makehash():
    return collections.defaultdict(makehash)


class NotificationTester(Notification):

    def __init__(self, container):
        super().__init__(container)
        self.notifications = makehash()

    def send_or_queue(
        self,
        notifiable,
        notification,
        notification_id,
        channel_instance,
        dry=False,
        fail_silently=False,
    ):
        """Fake sending notifications by saving instead in a a specific structure allowing
        to make different assertions on it later."""
        if not notification.id:
            notification.id = notification_id
        data = {
            "notification": notification,
            "channels": channel_instance,
            "notifiable": notifiable,
            "dry": dry,
            "fail_silently": fail_silently
        }

        if (isinstance(notifiable, AnonymousNotifiable)):
            notifiable_id = list(notifiable._routes.values())[0]
            # notifiable_channel = list(notifiable._routes.keys())[0]
            path = f"__anonymous__.{notifiable_id}.{notification.__class__.__name__}"
        else:
            notifiable_id = notifiable.get_primary_key_value()
            path = f"{notifiable.__class__.__name__}.{notifiable_id}.{notification.__class__.__name__}"

        notifs = deep_get(self.notifications, path)
        if notifs:
            notifs.append(data)
        else:
            self.notifications[path.split(".")[0]][str(notifiable_id)][str(notification.__class__.__name__)] = [data]

    def assertNothingSent(self):
        """Assert no notifications has been sent since last call to Notifications.fake()."""
        assert not self.notifications

    def assertSentTo(self, notifiables, notification_class, test_method=None, count=1):
        """
            Assert a notification <notification_class> has been sent to the given notifiables once
            or count times.
            In addition assert that the notification is passing the given test if provided.

            notifiables: user, [user1, user2], 'test@.email.com', '#general
        """
        if not isinstance(notifiables, list):
            notifiables = [notifiables]
        for notifiable in notifiables:
            if (isinstance(notifiable, Notifiable)):
                user_notifs = self.notifications[str(notifiable.__class__.__name__)][str(notifiable.get_primary_key_value())]
            else:
                notifiable_key = notifiable
                user_notifs = self.notifications["__anonymous__"][notifiable_key]
            # check that {count} notification of type {notification_class} have been sent
            user_notifs_of_type = user_notifs.get(str(notification_class.__name__), [])
            assert len(user_notifs_of_type) == count
            # check that the first notification is passing the test
            if test_method:
                test_notification = user_notifs_of_type[0]
                assert test_method(notifiable, test_notification["notification"], test_notification["channels"])

    def notificationsFor(self, notifiable, notification_class=None):
        if (isinstance(notifiable, Notifiable)):
            try:
                all_notifs = self.notifications[str(notifiable.__class__.__name__)][str(notifiable.get_primary_key_value())]
            except KeyError:
                return []
        else:
            try:
                all_notifs = self.notifications["__anonymous__"][notifiable]
            except KeyError:
                return []
        # filter by notification type
        if notification_class:
            all_notifs = all_notifs.get(str(notification_class.__name__), [])
        return list(map(lambda obj: obj["notification"], all_notifs))
