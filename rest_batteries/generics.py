from typing import Optional, Type

from django.core.exceptions import ImproperlyConfigured
from rest_framework import generics
from rest_framework.serializers import BaseSerializer

from .mixins import (
    APIErrorsMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericAPIView(APIErrorsMixin, generics.GenericAPIView):
    request_serializer_class: Optional[Type[BaseSerializer]] = None
    destroy_request_serializer_class: Optional[Type[BaseSerializer]] = None
    response_serializer_class: Optional[Type[BaseSerializer]] = None

    def get_request_serializer(self, *args, **kwargs) -> BaseSerializer:
        serializer = self.get_request_serializer_or_none(*args, **kwargs)
        if serializer is None:
            self.raise_request_serializer_error()
        return serializer

    def get_request_serializer_or_none(
        self, *args, **kwargs
    ) -> Optional[BaseSerializer]:
        serializer_class = self.get_request_serializer_class_or_none()
        if serializer_class is not None:
            kwargs.setdefault('context', self.get_request_serializer_context())
            return serializer_class(*args, **kwargs)

    def get_request_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        if self.request.method == 'DELETE':
            return self.destroy_request_serializer_class
        return self.request_serializer_class

    def get_request_serializer_context(self):
        return self.get_serializer_context()

    def raise_request_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure `request_serializer_class` attribute'
        )

    def get_response_serializer(self, *args, **kwargs) -> BaseSerializer:
        serializer = self.get_response_serializer_or_none(*args, **kwargs)
        if serializer is None:
            self.raise_response_serializer_error()
        return serializer

    def get_response_serializer_or_none(
        self, *args, **kwargs
    ) -> Optional[BaseSerializer]:
        serializer_class = self.get_response_serializer_class_or_none()
        if serializer_class is not None:
            kwargs.setdefault('context', self.get_response_serializer_context())
            return serializer_class(*args, **kwargs)

    def get_response_serializer_class_or_none(self) -> Optional[Type[BaseSerializer]]:
        return self.response_serializer_class

    def get_response_serializer_context(self):
        return self.get_serializer_context()

    def raise_response_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure `response_serializer_class` attribute'
        )

    def get_serializer_class(self) -> Type[BaseSerializer]:
        response_serializer_class = self.get_response_serializer_class_or_none()
        if response_serializer_class is not None:
            return response_serializer_class

        if self.serializer_class is not None:
            return self.serializer_class

        self.raise_serializer_error()

    def raise_serializer_error(self):
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} should properly configure one of these attributes: '
            f'`response_serializer_class`, `serializer_class`'
        )


# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.


class CreateAPIView(CreateModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(ListModelMixin, GenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(RetrieveModelMixin, GenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(DestroyModelMixin, GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(UpdateModelMixin, GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(RetrieveModelMixin, UpdateModelMixin, GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(RetrieveModelMixin, DestroyModelMixin, GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericAPIView
):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
