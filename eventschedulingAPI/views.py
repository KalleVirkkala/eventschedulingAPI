from django.views.generic.base import RedirectView


class BaseRedirectView(RedirectView):
    url = "/api/v1/"
