"""Mail Component Class."""

from masonite import Queue, Mail
from masonite.queues import ShouldQueue
from ..exceptions import InvalidNotificationType

from config import mail


class MailComponent:
    template = ''
    _driver = None
    _run = True
    template_prefix = '/masonite/notifications'

    def __init__(self, app):
        """Mail Component Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        self._view = self.app.make('View')
        self._subject = None

    def line(self, message):
        """Writes a line to a template.

        Arguments:
            message {string} -- The message text to show.

        Returns:
            self
        """
        self.template += self._view(self.template_prefix + '/snippets/mail/line',
                                    {'message': message}).rendered_template
        return self

    def action(self, message, href=None, style='success'):
        """Shows an action button.

        Arguments:
            message {string} -- The text to show inside the button.

        Keyword Arguments:
            href {string} -- The URL the button should go to (default: {None})
            style {string} -- The style of the button. This changes the color. (default: {'success'})

        Returns:
            self
        """
        self.template += self._view(self.template_prefix + '/snippets/mail/action',
                                    {'message': message, 'style': style, 'href': href}).rendered_template
        return self

    def view(self, template, dictionary={}):
        """Injects a template into the text.

        Arguments:
            template {string} -- The template to use.

        Keyword Arguments:
            dictionary {dict} -- Variables to pass to the template. (default: {{}})

        Returns:
            self
        """
        self.template += self._view(template, dictionary).rendered_template
        return self

    def panel(self, message):
        """Shows a panel well.

        Arguments:
            message {string} -- The text to show inside the panel well.

        Returns:
            self
        """
        self.template += self._view(self.template_prefix + '/snippets/mail/panel',
                                    {'message': message}).rendered_template
        return self

    def heading(self, message):
        """Shows a heading.

        Arguments:
            message {string} -- What text should show inside the heading.

        Returns:
            self
        """
        self.template += self._view(self.template_prefix + '/snippets/mail/heading',
                                    {'message': message}).rendered_template
        return self

    def subject(self, message):
        """Sets the subject of the email.

        Arguments:
            message {string} -- The text to show as the email header.

        Returns:
            self
        """
        self._subject = message
        return self

    def dry(self):
        """Sets whether the email should be sent or not.

        Returns:
            self
        """
        self._run = False
        return self

    def driver(self, driver):
        """Specifies the driver to use.

        Arguments:
            driver {string} -- The name of the driver.

        Returns:
            self
        """
        self._driver = driver
        return self

    def mail(self):
        """Used to show a not implemented type exception.

        Raises:
            Exception
        """
        raise Exception(
            'The {} notification does not have a mail method'.format(self))

    def fire_mail(self):
        """Used to fire the actual email and run the logic for sending emails.
        """
        driver = mail.DRIVER if not self._driver else None
        if self._run:
            if isinstance(self, ShouldQueue):
                self.app.make(Queue).push(self.app.make('Mail')
                                          .driver(driver)
                                          .to(self._to)
                                          .subject(self._subject)
                                          .send, args=(self.template,))
            else:
                self.app.make('Mail') \
                    .driver(driver) \
                    .to(self._to) \
                    .subject(self._subject) \
                    .send(self.template)
