"""Slack Component."""

import json

import requests
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
        """Specifies the text to be sent in the message.

        Arguments:
            message {string} -- The text to show in the message.

        Returns:
            self
        """
        self._text = message
        return self

    def channel(self, channel):
        """Specifies the channel to send the message to.

        Arguments:
            channel {string} -- The channel to send the message to.

        Returns:
            self
        """
        if channel.startswith('#'):
            self._channel = self.find_channel(channel)
        else:
            self._channel = channel

        return self

    def token(self, token):
        """Specifes the token to use for Slack authentication.

        Arguments:
            token {string} -- The Slack authentication token.

        Returns:
            self
        """
        self._token = token
        return self

    def as_user(self, username):
        """Specifies the user to send the message as.

        Arguments:
            username {string} -- The username to send the message as.

        Returns:
            self
        """
        self._username = username
        return self

    def icon(self, emoji):
        """The emoji as the icon to send.

        Arguments:
            emoji {string} -- The emoji to use.

        Returns:
            self
        """
        self._icon_emoji = emoji
        return self

    def as_current_user(self):
        """Sets the boolean on whether to use the currently authenticated user as the message.

        This is found using the token that is used for authentication.

        Returns:
            self
        """
        self._as_current_user = True
        return self

    def without_markdown(self):
        """Specifies whether the message should explicitly not honor markdown text.

        Returns:
            self
        """
        self._mrkdwn = False
        return self

    def dont_unfurl(self):
        """Whether the message should unfurl any media message.

        Unfurling is when it shows a bigger part of the message after the text is sent
        like when pasting a link and it showing the header images.

        Returns:
            self
        """
        self._unfurl = False
        return self

    def can_reply(self):
        """Whether the message should be ably to be replied back to.

        Returns:
            self
        """
        self._reply_broadcast = True
        return self

    def as_snippet(self, file_type='python', name='snippet', title='My Snippet'):
        """Whether the current message should be sent as a snippet or not.

        Keyword Arguments:
            file_type {string} -- The type of the snippet. (default: {'python'})
            name {string} -- The name of the snippet. (default: {'snippet'})
            title {string} -- The title of the snippet. (default: {'My Snippet'})

        Returns:
            self
        """
        self._as_snippet = True
        self._snippet_name = name
        self._type = file_type
        self._title = title
        return self

    def comment(self, comment):
        """Sets the initial comment on the message.

        Arguments:
            comment {string} -- The text of the comment.

        Returns:
            self
        """
        self._initial_comment = comment
        return self

    def button(self, text, url, **options):
        """Shows an action button to use.

        Arguments:
            text {string} -- The text to show inside the button.
            url {string} -- The url the button should go back to.

        Returns:
            self
        """
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
        """Whether the message should actually be sent or not.

        Returns:
            self
        """
        self._run = False
        return self

    def attach(self, file): 
        pass

    def thumbnail(self, location): 
        pass

    def dont_link(self):
        pass

    def find_channel(self, name):
        """Calls the Slack API to find the channel name. 

        This is so we do not have to specify the channel ID's. Slack requires channel ID's
        to be used.

        Arguments:
            name {string} -- The channel name to find.

        Raises:
            SlackChannelNotFound -- Thrown if the channel name is not found.

        Returns:
            self
        """
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
        """Throws a not implemented type exception.

        Raises:
            Exception
        """
        raise Exception(
            'The {} notification does not have a slack method'.format(self))

    def fire_slack(self):
        """Internal class to be called to run the logic and actually fire the Slack message.
        """
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
