from django.core.exceptions import ValidationError
from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updates = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EventDateData(BaseModel):
    objects = None
    date_suggestion = models.DateField()

    def __unicode__(self):
        return self.date_suggestion


class Event(BaseModel):
    objects = None
    name = models.CharField(max_length=255)
    dates = models.ManyToManyField(EventDateData, related_name="event_dates")

    def clean(self):
        raise ValidationError('Problem during validation')

    def __str__(self):
        return self.name

    @property
    def get_all_event_votes(self):
        return Votes.objects.filter(event=self)

    @property
    def get_all_people(self):
        return People.objects.filter(event=self)

    @callable
    def get_all_votes_for_date(self):
        return Votes.objects.filter(event=self)


class People(BaseModel):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Votes(BaseModel):
    objects = None

    user = models.ForeignKey(People, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_voted = models.ForeignKey(EventDateData, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.date_voted


