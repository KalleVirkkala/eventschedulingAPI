from rest_framework.authtoken.models import Token

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--user_id", type=int)

    def handle(self, *args, **options):
        user = options["user_id"]
        token = Token.objects.create(user_id=user)
        print(token.key)

