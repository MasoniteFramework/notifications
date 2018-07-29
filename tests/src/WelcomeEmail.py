from notifications import Notifiable

class WelcomeNotification(Notifiable):

    def __init__(self, Request):
        self.request = Request

    def mail(self, driver=None):
        self.subject('New account signup!') \
            .panel('GBALeague.com') \
            .heading('You have created a new account!') \
            .line('We greatly value your service!') \
            .line('Attached is an invoice for your recent purchase') \
            .action('Sign Back In')

    def slack(self, token=None):
        self.text('A new user registered') \
            .channel('#general') \
            .channel(['#general', '#random']) \
            .as_user('Bot User') \
            .as_current_user() \
            .attach('storage/images/file.png') \
            .icon('thumbsup') \
            .thumbnail('storage/logos/logo.png') \
            .dont_link() \
            .as_markdown() \
            .no_reply() \


Notify.mail(
    WelcomeNotification,
    PromotionNotification,
    to='email@email.com'
)
