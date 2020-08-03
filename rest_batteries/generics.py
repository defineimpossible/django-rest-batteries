from rest_framework import generics

from .mixins import APIErrorsMixin


class GenericAPIView(APIErrorsMixin, generics.GenericAPIView):
    pass
