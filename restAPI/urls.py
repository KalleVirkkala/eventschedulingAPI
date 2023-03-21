from django.urls import include, path
from rest_framework import routers
from .views import EventViewSet, EventListViewSet

urlpatterns = [
    path(r'event/list/', EventListViewSet.as_view(), name='event-list'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

router = routers.DefaultRouter()
router.register(r'event', EventViewSet)
urlpatterns += router.urls



