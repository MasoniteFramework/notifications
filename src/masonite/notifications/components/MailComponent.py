"""Mail Component Class."""


class MailComponent:
    template = ''
    template_prefix = '/src/masonite/notifications'

    def __init__(self):
        """Mail Component Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        from wsgi import container
        self.app = container
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
