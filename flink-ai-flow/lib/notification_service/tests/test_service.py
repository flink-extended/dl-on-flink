import unittest

from notification_service.event_storage import DbEventStorage
from notification_service.mongo_event_storage import MongoEventStorage
from notification_service.service import NotificationService


class NotificationServiceTest(unittest.TestCase):

    def test_from_storage_uri(self):
        service = NotificationService.from_storage_uri("sqlite:///aiflow.db")
        self.assertTrue(isinstance(service.storage, DbEventStorage))
        service = NotificationService.from_storage_uri("mongodb://user:pass@localhost:27017/test")
        self.assertTrue(isinstance(service.storage, MongoEventStorage))
