"""Notifications Settings."""
from masonite import env

"""
Nexmo notifications driver settings.
"""

NEXMO = {
    'key': env('NEXMO_KEY', ""),
    'secret': env('NEXMO_SECRET', ""),
    'sms_from': env('NEXMO_SMS_FROM', "+33000000000")
}