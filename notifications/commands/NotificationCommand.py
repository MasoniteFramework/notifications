""" A NotificationCommand Command """
from cleo import Command
import os


class NotificationCommand(Command):
    """
    Creates a notification class.

    notification
        {name : Name of the notification to create.}
    """

    def handle(self):
        notification = self.argument('name')
        if not os.path.isfile('app/notifications/{0}.py'.format(notification)):
            if not os.path.exists(os.path.dirname('app/notifications/{0}.py'.format(notification))):
                # Create the path to the notification if it does not exist
                os.makedirs(os.path.dirname('app/notifications/{0}.py'.format(notification)))

            f = open('app/notifications/{0}.py'.format(notification), 'w+')

            f.write("''' A {0} Notification '''\n".format(notification))
            f.write('from notifications import Notifiable\n\n')
            f.write("class {0}(Notifiable):\n\n    def mail(self):\n        pass\n".format(notification))

            self.info('Notification Created Successfully!')
        else:
            self.error('Notification Already Exists!')