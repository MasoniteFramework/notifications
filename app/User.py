""" User Model """
from config.database import Model

from src.masonite.notifications import Notifiable


class User(Model, Notifiable):
    """User Model"""

    __fillable__ = ['name', 'email', 'password']

    __auth__ = 'email'
