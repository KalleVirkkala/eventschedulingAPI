import json

from django.utils.encoding import force_str
from rest_framework.authtoken.admin import User
from rest_framework.test import APITestCase
from tests.factories import create_token, EventFactory, EventDateDataFactory, \
    VotesFactory, PeopleFactory


class EventApiTestCase(APITestCase):

    def assertContainsKeys(self, data, *keys):  # NOQA
        for key in keys:
            self.assertTrue(key in data, "key '%s' missing from data" % key)


class ApiAuthenticationTokenTest(EventApiTestCase):

    def test_access_api_token_not_set(self):
        resp = self.client.get("/api/v1/")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(
            json.loads(resp.content)["detail"],
            "Authentication credentials were not provided.",
        )

    def test_access_api_token_set(self):
        user = User.objects.create_user(
            'user01', 'user01@example.com', 'user01P4ssw0rD')
        token = create_token(user)
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(token))
        resp = self.client.get("/api/v1/")
        self.assertEqual(resp.status_code, 200)
        self.assertContainsKeys(
            resp.data,
            "event",
        )


class AuthenticatedEventAPITestCase(EventApiTestCase):

    def setUp(self):
        user = User.objects.create_user(
            'user01', 'user01@example.com', 'user01P4ssw0rD')
        self.token = create_token(user)
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.token.key))


class EventSchedulingBaseApiTests(AuthenticatedEventAPITestCase):

    def test_list_events(self):
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        EventFactory(dates=[event_date])
        resp = self.client.get("/api/v1/event/list/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '"name":"The Greatest Event"', status_code=200, )

    def test_create_event(self):
        data = {"name": "My test Event",
                "dates": ["2023-05-10", "2023-05-12"]}

        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '"id":1')

    def test_update_event(self):
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event = EventFactory(dates=[event_date])
        self.assertEqual(event.name, "The Greatest Event")

        data = {"name": "My updated Event",
                "dates": ["2023-05-15", "2023-05-17"]}

        resp = self.client.put("/api/v1/event/{}/".format(event.id), data)
        self.assertEqual(resp.status_code, 200)
        self.assertContainsKeys(resp.data, "id")
        self.assertContains(resp, '"id":1', status_code=200,)

    def test_delete_event(self):
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event = EventFactory(dates=[event_date])

        resp = self.client.delete("/api/v1/event/{}/".format(event.id))
        self.assertEqual(resp.status_code, 204)
        self.assertContainsKeys(resp.data, "id")
        self.assertContains(resp, '"id":1', status_code=200,)

    def test_create_event_no_name(self):
        data = {"dates": ["2023-05-10", "2023-05-12"]}
        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 400)
        self.assertContains(
            resp,
            'This field is required.',
            status_code=400,
        )
        data["name"] = ""
        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 400)
        self.assertContains(
            resp,
            'This field may not be blank',
            status_code=400,
        )

    def test_create_event_no_dates(self):
        data = {"name": "My test Event"}

        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 400)
        self.assertContains(
            resp,
            'This field is required.',
            status_code=400,
        )
        data["dates"] = ""
        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 400)
        self.assertContains(
            resp,
            'Dates cannot be blank or is not a list of dates',
            status_code=400,
        )

    def test_create_event_wrong_date_format(self):
        data = {"name": "My test Event",
                "dates": ["2023/05/10", "2023-05-12"]}

        resp = self.client.post("/api/v1/event/", data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(force_str(resp.content),
                         '["Incorrect date format, should be YYYY-MM-DD"]')

    def test_create_vote(self):
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event = EventFactory(dates=[event_date])

        data = {"name": "Karl",
                "votes": ["2023-05-10"]}

        resp = self.client.post("/api/v1/event/{}/vote/".format(event.id), data)
        self.assertEqual(resp.status_code, 201)
        self.assertContains(
            resp,
            'votes":[{"date":"2023-05-10","people":["Karl"]}]',
            status_code=201,
        )

    def test_create_vote_wrong_date(self):

        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event = EventFactory(dates=[event_date])
        data = {"name": "Karl",
                "votes": ["2023-05-12"]}

        resp = self.client.post("/api/v1/event/{}/vote/".format(event.id), data)
        self.assertEqual(resp.status_code, 400)
        self.assertContains(
            resp,
            'Voted date does not exist for event',
            status_code=400,
        )

    def test_results_no_suitable_dates(self):
        # create event
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event_date2 = EventDateDataFactory(date_suggestion="2023-05-15")
        event_date3 = EventDateDataFactory(date_suggestion="2023-05-18")
        event = EventFactory(dates=[event_date, event_date2, event_date3])

        # create people
        voter = PeopleFactory(event=event)
        voter2 = PeopleFactory(event=event)
        voter3 = PeopleFactory(event=event)

        # create votes
        VotesFactory(date_voted=event_date3, user=voter, event=event)
        VotesFactory(date_voted=event_date2, user=voter2, event=event)
        VotesFactory(date_voted=event_date2, user=voter3, event=event)

        resp = self.client.get("/api/v1/event/{}/results/".format(event.id))
        self.assertEqual(resp.status_code, 200)
        print(resp.content)
        self.assertContains(
            resp,
            [],
            status_code=200,
        )

    def test_results_suitable_dates(self):
        # create event
        event_date = EventDateDataFactory(date_suggestion="2023-05-10")
        event_date2 = EventDateDataFactory(date_suggestion="2023-05-15")
        event_date3 = EventDateDataFactory(date_suggestion="2023-05-18")
        event = EventFactory(dates=[event_date, event_date2, event_date3])

        # create people
        voter = PeopleFactory(event=event)
        voter2 = PeopleFactory(event=event)
        voter3 = PeopleFactory(event=event)

        # create votes
        VotesFactory(date_voted=event_date2, user=voter, event=event)
        VotesFactory(date_voted=event_date2, user=voter2, event=event)
        VotesFactory(date_voted=event_date2, user=voter3, event=event)
        VotesFactory(date_voted=event_date3, user=voter2, event=event)
        VotesFactory(date_voted=event_date, user=voter, event=event)
        VotesFactory(date_voted=event_date, user=voter2, event=event)
        VotesFactory(date_voted=event_date, user=voter3, event=event)

        resp = self.client.get("/api/v1/event/{}/results/".format(event.id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp,
            event_date.date_suggestion,
            status_code=200,
        )
        self.assertContains(
            resp,
            event_date2.date_suggestion,
            status_code=200,
        )
