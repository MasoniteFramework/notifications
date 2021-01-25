"""Notifications Settings."""
from masonite import env

"""
Slack notifications driver settings.
"""

SLACK = {"token": env("SLACK_TOKEN", "")}

"""
Vonage notifications driver settings.
"""

VONAGE = {
    "key": env("VONAGE_KEY", ""),
    "secret": env("VONAGE_SECRET", ""),
    "sms_from": env("VONAGE_SMS_FROM", "+33000000000"),
}
