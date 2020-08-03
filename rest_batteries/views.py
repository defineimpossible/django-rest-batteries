from rest_framework import views

from .mixins import APIErrorsMixin


class APIView(APIErrorsMixin, views.APIView):
    pass
