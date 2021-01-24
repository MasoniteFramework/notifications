"""Slack Component Class"""
import json
from .BaseComponent import BaseComponent

from ..exceptions import NotificationFormatError


class SlackComponent(BaseComponent):
    def __init__(self):
        super().__init__()
        self._text = ""
        self._username = "masonite-bot"
        self._icon_emoji = ""
        self._icon_url = ""
        self._channel = ""
        self._text = ""
        self._mrkdwn = True
        self._as_current_user = False
        self._reply_broadcast = False
        self._token = ""
        # Indicates if channel names and usernames should be linked.
        self._link_names = False
        # Indicates if you want a preview of links inlined in the message.
        self._unfurl_links = False
        # Indicates if you want a preview of links to media inlined in the message.
        self._unfurl_media = False
        self._blocks = []
        self._colors = {"success": "good", "error": "danger", "warning": "warning"}

    def send_from(self, username, icon=None, url=None):
        """Set a custom username and optional emoji icon for the Slack message."""
        self._username = username
        if icon:
            self._icon_emoji = icon
        elif url:
            self._icon_url = url
        return self

    def to(self, channel):
        """Specifies the channel to send the message to. It can be either
        a channel ID or a channel name (with #).

        Arguments:
            channel {string} -- The channel to send the message to.

        Returns:
            self
        """
        self._channel = channel
        return self

    def text(self, text):
        """Specifies the text to be sent in the message.

        Arguments:
            text {string} -- The text to show in the message.

        Returns:
            self
        """
        self._text = text
        return self

    def link_names(self):
        """Find and link channel names and usernames in message."""
        self._link_names = True
        return self

    def unfurl_links(self):
        """Whether the message should unfurl any links.

        Unfurling is when it shows a bigger part of the message after the text is sent
        like when pasting a link and it showing the header images.

        Returns:
            self
        """
        self._unfurl_links = True
        self._unfurl_media = True
        return self

    def as_dict(self):
        return {
            "text": self._text,
            # this one is overriden when using api mode
            "channel": self._channel,
            # optional
            "link_names": self._link_names,
            "unfurl_links": self._unfurl_links,
            "unfurl_media": self._unfurl_media,
            "username": self._username,
            "as_user": self._as_current_user,
            "icon_emoji": self._icon_emoji,
            "icon_url": self._icon_url,
            "mrkdwn": self._mrkdwn,
            "reply_broadcast": self._reply_broadcast,
            "blocks": json.dumps([block._resolve() for block in self._blocks]),
        }

    def token(self, token):
        """[API_MODE only] Specifies the token to use for Slack authentication.

        Arguments:
            token {string} -- The Slack authentication token.

        Returns:
            self
        """
        self._token = token
        return self

    def as_current_user(self):
        """[API_MODE only] Send message as the currently authenticated user.

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

    def can_reply(self):
        """Whether the message should be ably to be replied back to.

        Returns:
            self
        """
        self._reply_broadcast = True
        return self

    def block(self, block_instance):
        from slackblocks.blocks import Block

        if not isinstance(block_instance, Block):
            raise NotificationFormatError("Blocks should be imported from slackblocks.")
        self._blocks.append(block_instance)
        return self

    # def as_snippet(self, file_type='python', name='snippet', title='My Snippet'):
    #     """Whether the current message should be sent as a snippet or not.

    #     Keyword Arguments:
    #         file_type {string} -- The type of the snippet. (default: {'python'})
    #         name {string} -- The name of the snippet. (default: {'snippet'})
    #         title {string} -- The title of the snippet. (default: {'My Snippet'})

    #     Returns:
    #         self
    #     """
    #     self._as_snippet = True
    #     self._snippet_name = name
    #     self._type = file_type
    #     self._title = title
    #     return self

    # def comment(self, comment):
    #     """Sets the initial comment on the message.

    #     Arguments:
    #         comment {string} -- The text of the comment.

    #     Returns:
    #         self
    #     """
    #     self._initial_comment = comment
    #     return self
