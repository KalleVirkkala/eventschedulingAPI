from django.test import TestCase
from .factories import EventFactory, PeopleFactory


class EventTestCase(TestCase):
    def test_str(self):
        event = EventFactory()
        self.assertEqual(str(event), event.name)


class PeopleTestCase(TestCase):
    def test_str(self):
        people = PeopleFactory()
        self.assertEqual(str(people), people.name)
