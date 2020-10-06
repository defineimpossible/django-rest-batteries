from rest_framework import views

from .mixins import DjangoValidationErrorTransformMixin


class APIView(DjangoValidationErrorTransformMixin, views.APIView):
    pass
