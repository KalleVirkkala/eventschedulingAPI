from django.contrib import admin

# Register your models here.
from restAPI.models import *


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_dates', 'created', 'updates')

    def get_dates(self, obj):
        if obj.dates.all():
            return ",\n".join([str(d.date_suggestion) for d in obj.dates.all()])

    get_dates.short_description = 'Event dates'


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_date_voted', 'created', 'updates')

    def get_date_voted(self, obj):
        return str(obj.date_voted.date_suggestion)

    get_date_voted.short_description = 'Date voted'


class PeopleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'event', 'created', 'updates')


admin.site.register(Event, EventAdmin)
admin.site.register(EventDateData)

admin.site.register(People, PeopleAdmin)
admin.site.register(Votes, VoteAdmin)
