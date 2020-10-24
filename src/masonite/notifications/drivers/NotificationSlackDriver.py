"""Slack Component."""
import json
import requests
from masonite.app import App
from masonite.drivers import BaseDriver

from ..exceptions import SlackChannelNotFound, SlackInvalidMessage, SlackInvalidWorkspace, SlackPostForbidden, SlackChannelArchived, \
    SlackInvalidWebhook
from ..NotificationContract import NotificationContract


class NotificationSlackDriver(BaseDriver, NotificationContract):

    app = None
    WEBHOOK_MODE = 1
    API_MODE = 2
    sending_mode = WEBHOOK_MODE

    def __init__(self, app: App):
        """Slack Driver Constructor.

        Arguments:
            app {masonite.app.App} -- The Masonite container object.
        """
        self.app = app
        self._debug = True

    def send(self, notifiable, notification):
        """Used to send the email and run the logic for sending emails."""
        data = self.get_data("slack", notifiable, notification)
        recipients = self.get_recipients(notifiable, notification)
        if self.sending_mode == self.WEBHOOK_MODE:
            self.send_via_webhook(data, recipients)
        else:
            self.send_via_api(data, recipients)

    def get_recipients(self, notifiable, notification):
        """Get recipients which can be defined through notifiable route method.
        For Slack it can be:
            - an incoming webhook (or a list of incoming webhooks) that you defined in your app OR
            return webhook_url
            return [webhook_url_1, webhook_url_2]
            - a channel name or ID (it will use Slack API and requires a Slack token
            for accessing your workspace)
            return "{channel_name or channel_id}"
            return [channel_name_1, channel_name_2]
        You cannot mix both.
        """
        recipients = notifiable.route_notification_for("slack", notification)
        # multiple recipients
        if isinstance(recipients, list):
            _modes = []
            for recipient in recipients:
                _modes.append(self._check_recipient_type(recipient))
            if self.API_MODE in _modes and self.WEBHOOK_MODE in _modes:
                raise ValueError("NotificationSlackDriver: sending mode cannot be mixed.")
        else:
            mode = self._check_recipient_type(recipients)
            self.sending_mode = mode
            recipients = [recipients]
        return recipients

    def _check_recipient_type(self, recipient):
        if recipient.startswith("https://hooks.slack.com"):
            return self.WEBHOOK_MODE
        else:
            return self.API_MODE

    def send_via_webhook(self, payload, webhook_urls):
        data = json.dumps(payload.as_dict())
        if self._debug:
            print(data)
        for webhook_url in webhook_urls:
            response = requests.post(
                webhook_url, data=data,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                self._handle_webhook_error(response, payload)

    def send_via_api(self, payload, channels):
        # TODO: fetch token, from env ?
        # TODO: implement this one
        # data =
        for channel in channels:
            pass
            # if notification._as_snippet:
            #     requests.post('https://slack.com/api/files.upload', {
            #         'token': notification._token,
            #         'channel': channel,
            #         'content': notification._text,
            #         'filename': notification._snippet_name,
            #         'filetype': notification._type,
            #         'initial_comment': notification._initial_comment,
            #         'title': notification._title,
            #     })
            # else:
            #     requests.post('https://slack.com/api/chat.postMessage', {
            #         'token': notification._token,
            #         'channel': channel,
            #         'text': notification._text,
            #         'username': notification._username,
            #         'icon_emoji': notification._icon_emoji,
            #         'as_user': notification._as_current_user,
            #         'mrkdwn': notification._mrkdwn,
            #         'reply_broadcast': notification._reply_broadcast,
            #         'unfurl_links': notification._unfurl,
            #         'unfurl_media': notification._unfurl,
            #         'attachments': json.dumps(notification._attachments),
            #     })

    def _handle_webhook_error(self, response, payload):
        if response.text == "invalid_payload":
            raise SlackInvalidMessage(
                "The message is malforme: perhaps the JSON is structured incorrectly, or the message text is not properly escaped."
            )
        elif response.text == "too_many_attachments":
            raise SlackInvalidMessage(
                "Too many attachments: the message can have a maximum of 100 attachments associated with it."
            )
        elif response.text == "channel_not_found":
            raise SlackChannelNotFound(
                "The user or channel being addressed either do not exist or is invalid: {}".format(payload._channel)
            )
        elif response.text == "channel_is_archived":
            raise SlackChannelArchived(
                "The channel being addressed has been archived and is no longer accepting new messages: {}".format(payload._channel)
            )
        elif response.text in ["action_prohibited", "posting_to_general_channel_denied"]:
            raise SlackPostForbidden(
                "You don't have the permission to post to this channel right now: {}".format(payload._channel)
            )
        elif response.text in ["no_service", "no_service_id"]:
            raise SlackInvalidWebhook(
                "The provided incoming webhook is either disabled, removed or invalid."
            )
        elif response.text in ["no_team", "team_disabled"]:
            raise SlackInvalidWorkspace(
                "The Slack workspace is no longer active or is missing or invalid."
            )
    # def serialize_data(self, data):
    #     return json.dumps(data)

    # def build_payload(self, notifiable, notification):
    #     # TODO: if notifiable is not instance of Model it won't work ...
    #     # TODO: if notifiable PK is not integer it won't work ...
    #     return {
    #         "id": str(notification.id),
    #         "type": notification.notification_type(),
    #         "notifiable_id": notifiable.id,
    #         "notifiable_type": notifiable.__class__.get_morph_name(),
    #         "data": self.serialize_data(self.get_data("database", notifiable, notification)),
    #         "read_at": None
    #     }

    # def find_channel(self, name):
    #     """Calls the Slack API to find the channel name.

    #     This is so we do not have to specify the channel ID's. Slack requires channel ID's
    #     to be used.

    #     Arguments:
    #         name {string} -- The channel name to find.

    #     Raises:
    #         SlackChannelNotFound -- Thrown if the channel name is not found.

    #     Returns:
    #         self
    #     """
    #     if self._run:
    #         response = requests.post('https://slack.com/api/channels.list', {
    #             'token': self._token
    #         })
    #         for channel in response.json()['channels']:
    #             if channel['name'] == name.split('#')[1]:
    #                 return channel['id']

    #         raise SlackChannelNotFound(
    #             'Could not find the {} channel'.format(name))
    #     else:
    #         return 'TEST_ID'
