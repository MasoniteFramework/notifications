from notifications.components import MailComponent, SlackComponent


class Notifiable(MailComponent, SlackComponent):
    pass
