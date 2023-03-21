from datetime import datetime
from django.db.models import Count
from rest_framework import serializers
from eventschedulingAPI import settings
from .models import Event, EventDateData, People, Votes


class EventDetailSerializer(serializers.ModelSerializer):

    dates = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()

    def get_dates(self, obj): # noqa
        event_dates = obj.dates.all()
        dates = list()
        for data in event_dates:
            dates.append(data.date_suggestion)
        return dates

    def get_votes(self, obj): # noqa
        votes = list()

        for data in obj.dates.all():
            people_list = list()
            people_date_votes = Votes.objects.filter(event=obj.id,
                                                     date_voted=data)
            for people in people_date_votes:
                people_list.append(people.user.name)

            if people_list:
                votes_dict = {"date": data.date_suggestion,
                              "people": people_list}
                votes.append(votes_dict)
        return votes

    class Meta:
        model = Event
        fields = ('id', 'name', 'dates', 'votes', )


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', )


class CreateNewEventSerializer(serializers.Serializer): # noqa

    name = serializers.CharField(required=True)
    dates = serializers.ListField(required=True)

    def validate_date(self, dates): # noqa

        # check for empty list or wrong date formats in list
        if dates == ['']:
            raise serializers.ValidationError(
                "Dates cannot be blank or is not a list of dates: [<date>, <date>]")
        for date in dates:
            try:
                datetime.strptime(date, settings.DATE_INPUT_FORMATS[0])
            except ValueError:
                raise serializers.ValidationError(
                    "Incorrect date format, should be YYYY-MM-DD")

    def create_event_data(self, date_data): # noqa
        date_list = list()
        for date in date_data:
            event_date = EventDateData(date_suggestion=date)
            date_list.append(event_date)
            event_date.save()
        return date_list

    def update(self, instance, validated_data):
        name = validated_data.get("name", instance.name)
        dates = validated_data.get("dates", instance.dates)

        self.validate_date(dates)
        event_dates = self.create_event_data(dates)
        instance.name = name
        instance.save()
        for event_date in event_dates:
            instance.dates.add(event_date)

        return instance

    def create(self, validated_data):
        name = validated_data.get("name")
        dates = validated_data.get("dates")

        self.validate_date(dates)
        event_dates = self.create_event_data(dates)
        event = Event(name=name)
        event.save()
        event.dates.set(event_dates)

        return event


class CreateVoteSerializer(serializers.Serializer): # noqa
    name = serializers.CharField(max_length=255, required=True)
    votes = serializers.ListField(required=False)

    def update(self, instance, validated_data):
        name = validated_data.get("name")
        votes = validated_data.get("votes")
        if not votes:
            raise serializers.ValidationError("Please add a date to the votes")

        if name not in instance.get_all_event_votes.values_list("user__name", flat=True):
            people = People(name=name, event=instance)
            people.save()
        else:
            people = People.objects.filter(event=instance, name=name).first()

        for date in votes:
            try:
                event_date = instance.dates.all().get(date_suggestion=date)
            except Exception:
                raise serializers.ValidationError("Voted date does not exist for event")
            vote = Votes.objects.filter(event=instance, user=people,
                                        date_voted=event_date.id)
            if not vote:
                votes = Votes(event=instance, user=people, date_voted=event_date)
                votes.save()

        return instance

    class Meta:
        model = Event
        fields = ()


class ResultSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False)
    suitabledates = serializers.SerializerMethodField()

    def get_suitabledates(self, obj): # noqa
        suitable_dates = list()
        # get all people for event
        all_people = list(obj.get_all_people.values_list("name", flat=True))
        # get all votes
        all_votes = list(obj.get_all_event_votes.values_list("date_voted", flat=True))

        if not all_votes:
            return "No votes accounted for"

        # get all dates with votes
        event_days_with_votes = EventDateData.objects.filter(id__in=all_votes)
        for event_date in event_days_with_votes:

            # check that all participants have voted on the date
            if sorted(all_people) == sorted(list(Votes.objects.filter(
                    date_voted=event_date).values_list("user__name", flat=True))):
                suitable_date = event_date

                # get the names of the people that votes
                people_votes = Votes.objects.filter(event=obj.id,
                                                    date_voted=suitable_date)\
                    .values_list('user__name', flat=True)

                result_dict = {"date": suitable_date.date_suggestion,
                               "people": people_votes}

                suitable_dates.append(result_dict)

        if suitable_dates:
            return suitable_dates
        else:
            return []

    class Meta:
        model = Event
        fields = ('id', 'name', 'suitabledates', )


# We can use this serializer to get the closest suitable
# date where most participants voted
class MostVotedDateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False)
    closest_suitable_date = serializers.SerializerMethodField()

    def get_closest_suitable_date(self, obj):  # noqa
        suitable_dates = list()
        # get all votes
        all_votes = list(obj.get_all_event_votes.values_list("date_voted", flat=True))
        # get all dates with votes
        event_days_with_votes = EventDateData.objects.filter(id__in=all_votes)

        # count the votes
        count_of_voted_days = event_days_with_votes.order_by().annotate(
            date_voted_count=Count('date_suggestion'))
        if count_of_voted_days:
            # get the day with most votes
            most_voted_date = count_of_voted_days.latest("date_voted_count")

            # get the names of the people that votes
            people_votes = Votes.objects.filter(event=obj.id,
                                                date_voted=most_voted_date) \
                .values_list('user__name', flat=True)
            if most_voted_date:
                result_dict = {"date": most_voted_date.date_suggestion,
                               "people": people_votes}

                suitable_dates.append(result_dict)
            else:
                suitable_dates.append("No suitable dates")
            return suitable_dates
        else:
            return "No votes accounted for"

    class Meta:
        model = Event
        fields = ('id', 'name', 'closest_suitable_date',)