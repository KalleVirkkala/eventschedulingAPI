import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from rest_framework.authtoken.models import Token
from restAPI.models import Event, People, EventDateData, Votes


def create_token(user):
    token = Token.objects.create(user_id=user.id)
    return token


class EventDateDataFactory(DjangoModelFactory):
    date_suggestion = Faker('date')

    class Meta:
        model = EventDateData


class EventFactory(DjangoModelFactory):
    name = "The Greatest Event"

    @factory.post_generation
    def dates(self, create, extracted, **kwargs):
        if create and extracted:
            for date in extracted:
                self.dates.add(date)

    class Meta:
        model = Event


class PeopleFactory(DjangoModelFactory):
    name = Faker('name')
    event = None

    class Meta:
        model = People


class VotesFactory(DjangoModelFactory):
    user = SubFactory(PeopleFactory)
    event = None
    date_voted = Faker('date')

    class Meta:
        model = Votes
