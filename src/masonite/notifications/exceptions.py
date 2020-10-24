# General notifications exceptions
class InvalidNotificationType(Exception):
    pass

class NotificationFormatError(Exception):
    pass

# Database driver exceptions

# Broadcast driver exceptions

# Mail driver exceptions

# Slack driver exceptions
# https://api.slack.com/messaging/webhooks#handling_errors
class SlackDriverException(Exception):
    pass

class SlackChannelNotFound(SlackDriverException):
    pass

class SlackChannelArchived(SlackDriverException):
    pass

class SlackPostForbidden(SlackDriverException):
    pass

class SlackInvalidWebhook(SlackDriverException):
    pass

class SlackInvalidWorkspace(SlackDriverException):
    pass

class SlackInvalidMessage(SlackDriverException):
    pass


# Nexmo driver exceptions
class NexmoDriverException(Exception):
    pass

class NexmoInvalidMessage(NexmoDriverException):
    pass
