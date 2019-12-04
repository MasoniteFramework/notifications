"""Notify Class."""

import json
import os

import requests
from masonite.app import App

from .exceptions import InvalidNotificationType


class Notify:

    called_notifications = []

    def __init__(self, container: App):
        """Notify constructor.

        Arguments:
            container {masonite.app.App} -- Masonite app container.
        """
        self.app = container

    def __getattr__(self, name):
        """Special method that will be used to call the same method on the notifiable class.

        For example when Notify(SomeNotifiable).mail() it will call the mail method on the
        notifiable class.

        Arguments:
            name {string} -- The method to call on the notifiable class.

        Returns:
            None
        """
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

    def via(self, *methods):
        self._via = methods
        return self

    def send(self, *notifications, **options):
        self.called_notifications = []
        for via in self._via:
            for obj in notifications:
                notification = obj(self.app)
                self.called_notifications.append(notification)

                # Set all keyword arguments as protected members
                for key, value in options.items():
                    setattr(notification, '_{}'.format(key), value)

                # Call the method on the notifcation class
                self.app.resolve(
                    getattr(notification, via)
                )

                # Resolve the fire method inherited from the component
                notification = self.app.resolve(
                    getattr(notification, 'fire_{}'.format(via))
                )

        return self
