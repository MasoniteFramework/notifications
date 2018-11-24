import requests
import json
from notifications.exceptions import SlackChannelNotFound


class SlackComponent:

    app = None
    _text = ''
    _channel = ''
    _as_user = True
    _username = 'My Bot'
    _as_current_user = False
    _icon_emoji = ''
    _mrkdwn = True
    _reply_broadcast = False
    _attachments = []
    _run = True
    _unfurl = True
    _as_snippet = False

    _attach = ''
    _dont_link = True
    _as_markdown = False

    def text(self, message):
        self._text = message
        return self

    def channel(self, channel):
        if channel.startswith('#'):
            self._channel = self.find_channel(channel)
        else:
            self._channel = channel

        return self

    def token(self, token):
        self._token = token
        return self

    def as_user(self, username):
        self._username = username
        return self

    def icon(self, emoji):
        self._icon_emoji = emoji
        return self

    def as_current_user(self):
        self._as_current_user = True
        return self

    def without_markdown(self):
        self._mrkdwn = False
        return self

    def dont_unfurl(self):
        self._unfurl = False
        return self

    def can_reply(self):
        self._reply_broadcast = True
        return self

    def as_snippet(self, file_type='python', name='snippet', title='My Snippet'):
        self._as_snippet = True
        self._snippet_name = name
        self._type = file_type
        self._title = title
        return self

    def comment(self, comment):
        self._initial_comment = comment
        return self

    def button(self, text, url, **options):
        additional = {}
        if options.get('confirm'):
            additional.update(options.get('confirm'))

        data = {
            "type": "button",
            "text": text,
            # "name": options.get('name', 'button'),
            "style": options.get('style', 'primary'),
            "url": url
        }.update(additional)

        if not self._attachments:
            self._attachments.append(
                {
                    "fallback": "Your device is not able to view button links.",
                    'actions': [
                        data
                    ]
                }
            )
        else:
            self._attachments[0]['actions'].append(data)
        return self

    def dry(self):
        self._run = False
        return self

    def attach(self, file): pass

    def thumbnail(self, location): pass

    def dont_link(self):
        pass

    def find_channel(self, name):
        if self._run:
            response = requests.post('https://slack.com/api/channels.list', {
                'token': self._token
            })
            for channel in response.json()['channels']:
                if channel['name'] == name.split('#')[1]:
                    return channel['id']

            raise SlackChannelNotFound(
                'Could not find the {} channel'.format(name))
        else:
            return 'TEST_ID'

    def slack(self):
        raise Exception(
            'The {} notification does not have a slack method'.format(self))

    def fire_slack(self):
        notification = self.app.resolve(self.slack)
        if notification._run:
            if notification._as_snippet:
                requests.post('https://slack.com/api/files.upload', {
                    'token': notification._token,
                    'channels': notification._channel,
                    'content': notification._text,
                    'filename': notification._snippet_name,
                    'filetype': notification._type,
                    'initial_comment': notification._initial_comment,
                    'title': notification._title,
                })
            else:
                requests.post('https://slack.com/api/chat.postMessage', {
                    'token': notification._token,
                    'channel': notification._channel,
                    'text': notification._text,
                    'username': notification._username,
                    'icon_emoji': notification._icon_emoji,
                    'as_user': notification._as_current_user,
                    'mrkdwn': notification._mrkdwn,
                    'reply_broadcast': notification._reply_broadcast,
                    'unfurl_links': notification._unfurl,
                    'unfurl_media': notification._unfurl,
                    'attachments': json.dumps(notification._attachments),
                })
