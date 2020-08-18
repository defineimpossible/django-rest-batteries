from typing import Dict, Optional, Type

from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from .generics import GenericAPIView
from .mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    request_action_serializer_classes: Dict[str, Type[BaseSerializer]] = None
    response_action_serializer_classes: Dict[str, Type[BaseSerializer]] = None

    def get_request_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        serializer_class = None

        if self.request_action_serializer_classes:
            serializer_class = self.request_action_serializer_classes.get(self.action)
            if serializer_class is None and self.action == 'partial_update':
                serializer_class = self.request_action_serializer_classes.get('update')

        if serializer_class is None:
            return super().get_request_serializer_class_or_none()

        return serializer_class

    def raise_request_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure `request_action_serializer_classes` attribute'
        )

    def get_response_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        serializer_class = None

        if self.response_action_serializer_classes:
            serializer_class = self.response_action_serializer_classes.get(self.action)
            if serializer_class is None and self.action == 'partial_update':
                serializer_class = self.response_action_serializer_classes.get('update')

        if serializer_class is None:
            return super().get_response_serializer_class_or_none()

        return serializer_class

    def raise_response_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure `response_action_serializer_classes` attribute'
        )

    def raise_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure one of these attributes: '
            f'`response_action_serializer_classes`, `serializer_class`'
        )


class ReadOnlyModelViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """

    pass


class ModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    pass
