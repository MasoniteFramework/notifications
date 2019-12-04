""" Providers Configuration File """

from masonite.providers import (
    AppProvider,
    SessionProvider,
    RouteProvider,
    StatusCodeProvider,
    MailProvider,
    QueueProvider,
    CsrfProvider,
    ViewProvider,
)

from src.masonite.notifications.providers import NotificationProvider

"""
|--------------------------------------------------------------------------
| Providers List
|--------------------------------------------------------------------------
|
| Providers are a simple way to remove or add functionality for Masonite
| The providers in this list are either ran on server start or when a
| request is made depending on the provider. Take some time to learn
| more about Service Providers in our documentation
|
"""


PROVIDERS = [
    # Framework Providers
    AppProvider,
    SessionProvider,
    RouteProvider,
    StatusCodeProvider,
    ViewProvider,
    QueueProvider,
    MailProvider,

    # Optional Framework Providers
    CsrfProvider,

    # Third Party Providers
    NotificationProvider,

    # Application Providers

]
