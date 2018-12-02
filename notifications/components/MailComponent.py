from notifications.exceptions import InvalidNotificationType
from config import mail
from masonite.queues import ShouldQueue
from masonite import Queue


class MailComponent:
    template = ''
    _driver = None
    _run = True

    def __init__(self, app):
        self.app = app
        self._view = self.app.make('View')
        self._subject = None

    def line(self, message):
        self.template += self._view('/notifications/snippets/mail/line',
                                    {'message': message}).rendered_template
        return self

    def action(self, message, href=None, style='success'):
        self.template += self._view('/notifications/snippets/mail/action',
                                    {'message': message, 'style': style, 'href': href}).rendered_template
        return self

    def view(self, template, dictionary={}):
        self.template += self._view(template, dictionary).rendered_template
        return self

    def panel(self, message):
        self.template += self._view('/notifications/snippets/mail/panel',
                                    {'message': message}).rendered_template
        return self

    def heading(self, message):
        self.template += self._view('/notifications/snippets/mail/heading',
                                    {'message': message}).rendered_template
        return self

    def subject(self, message):
        self._subject = message
        return self

    def dry(self):
        self._run = False
        return self

    def driver(self, driver):
        self._driver = driver
        return self

    def mail(self):
        raise Exception(
            'The {} notification does not have a mail method'.format(self))

    def fire_mail(self):
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
