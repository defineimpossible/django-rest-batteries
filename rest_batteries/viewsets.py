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

    def get_request_serializer(self, *args, **kwargs) -> BaseSerializer:
        serializer = self.get_request_serializer_or_none(*args, **kwargs)
        if serializer is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} should properly configure `request_action_serializer_classes` attribute'
            )
        return serializer

    def get_request_serializer_or_none(
        self, *args, **kwargs
    ) -> Optional[BaseSerializer]:
        serializer_class = self.get_request_serializer_class_or_none()
        if serializer_class is not None:
            kwargs.setdefault('context', self.get_request_serializer_context())
            return serializer_class(*args, **kwargs)

    def get_request_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        serializer_class = None

        if self.request_action_serializer_classes:
            serializer_class = self.request_action_serializer_classes.get(self.action)
            if serializer_class is None and self.action == 'partial_update':
                serializer_class = self.request_action_serializer_classes.get('update')

        return serializer_class

    def get_request_serializer_context(self):
        return self.get_serializer_context()

    def get_response_serializer(self, *args, **kwargs) -> BaseSerializer:
        serializer = self.get_response_serializer_or_none(*args, **kwargs)
        if serializer is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} should properly configure `response_action_serializer_classes` attribute'
            )
        return serializer

    def get_response_serializer_or_none(
        self, *args, **kwargs
    ) -> Optional[BaseSerializer]:
        serializer_class = self.get_response_serializer_class_or_none()
        if serializer_class is not None:
            kwargs.setdefault('context', self.get_response_serializer_context())
            return serializer_class(*args, **kwargs)

    def get_response_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        serializer_class = None

        if self.response_action_serializer_classes:
            serializer_class = self.response_action_serializer_classes.get(self.action)
            if serializer_class is None and self.action == 'partial_update':
                serializer_class = self.response_action_serializer_classes.get('update')

        return serializer_class

    def get_response_serializer_context(self):
        return self.get_serializer_context()

    def get_serializer_class(self) -> Type[BaseSerializer]:
        response_serializer_class = self.get_response_serializer_class_or_none()
        if response_serializer_class is not None:
            return response_serializer_class

        if self.serializer_class is not None:
            return self.serializer_class

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
