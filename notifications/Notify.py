from notifications.exceptions import InvalidNotificationType
import requests
import json
import os


class Notify:

    called_notifications = []

    def __init__(self, Container):
        self.app = Container
        self.mail_config = self.app.make('MailConfig')

    def __getattr__(self, name):
        self.called_notifications = []
        def method(*notifications, **options):

            for obj in notifications:
                notification = obj(self.app)
                self.called_notifications.append(notification)

                # Set all keyword arguments as protected members
                for key, value in options.items():
                    setattr(notification, '_{}'.format(key), value)
                
                # Call the method on the notifcation class
                self.app.resolve(
                    getattr(notification, name)
                )

                # Resolve the fire method inherited from the component
                notification = self.app.resolve(
                    getattr(notification, 'fire_{}'.format(name))
                )
                
        return method
