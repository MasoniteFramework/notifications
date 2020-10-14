from masonite.testing import TestCase
from src.masonite.notifications import Notify


class TestNotifyHandler(TestCase):

    def setUp(self):
        super().setUp()
        self.notify = Notify(self.container)

    def test_send_basic_notification(self):
        pass