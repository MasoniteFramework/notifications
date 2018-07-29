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
                for key, value in options.items():
                    setattr(notification, '_{}'.format(key), value)
                notification = self.app.resolve(
                    getattr(notification, 'fire_{}'.format(name))
                )
                
        return method
