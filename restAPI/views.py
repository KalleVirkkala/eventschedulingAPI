from collections import OrderedDict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import EventListSerializer, EventDetailSerializer, \
    CreateNewEventSerializer, CreateVoteSerializer, ResultSerializer, \
    MostVotedDateSerializer
from .models import Event


class StandardEventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('events', data)
        ]))


class EventViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = EventDetailSerializer
    queryset = Event.objects.all().order_by('id')

    def create(self, request, *args, **kwargs):
        serializer = CreateNewEventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.create(serializer.validated_data)
            return Response(
                {"id": event.id}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = CreateNewEventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.update(event, serializer.validated_data)
            return Response(
                {"id": event.id, "message": "Has been updated"}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            ret_json = {
                "message": "Event has been deleted",
                "event": {"id": instance.id, "name": instance.name},
            }
            for date in instance.dates.all():
                date.delete()
            instance.delete()
            return Response(ret_json, status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='vote', url_name='vote')
    def vote(self, request, pk):
        allowed_methods = ["POST"]

        if request.method not in allowed_methods:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        instance = self.get_object()
        serializer = CreateVoteSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.update(instance, serializer.data)
            return Response(EventDetailSerializer(instance).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='results', url_name='results')
    def results(self, request, pk):
        allowed_methods = ["GET"]

        if request.method not in allowed_methods:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        instance = self.get_object()
        serializer = ResultSerializer(instance, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='most-votes',
            url_name='most-votes')
    def most_votes(self, request, pk):
        allowed_methods = ["GET"]

        if request.method not in allowed_methods:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        instance = self.get_object()
        serializer = MostVotedDateSerializer(instance, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventListViewSet(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = EventListSerializer
    queryset = Event.objects.all().order_by('id')

    pagination_class = StandardEventPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'name']
