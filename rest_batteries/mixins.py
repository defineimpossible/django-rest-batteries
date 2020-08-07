from django.core import exceptions as django_exceptions
from rest_framework import exceptions as rest_exceptions
from rest_framework import status
from rest_framework.response import Response


class APIErrorsMixin:
    """
    Mixin that transforms Django and Python exceptions into rest_framework ones.
    Without this mixin, they return 500 status code which is not desired.
    """

    expected_exceptions = {
        ValueError: rest_exceptions.ValidationError,
        django_exceptions.ValidationError: rest_exceptions.ValidationError,
    }

    def handle_exception(self, exc):
        if isinstance(exc, tuple(self.expected_exceptions.keys())):
            drf_exception_class = self.expected_exceptions[exc.__class__]
            drf_exception = drf_exception_class(self._get_error_message(exc))

            return super().handle_exception(drf_exception)

        return super().handle_exception(exc)

    def _get_error_message(self, exc):
        if hasattr(exc, 'message_dict'):
            return exc.message_dict

        error_msg = self._get_first_matching_attr(exc, 'message', 'messages')

        if isinstance(error_msg, list):
            error_msg = ', '.join(error_msg)

        if error_msg is None:
            error_msg = str(exc)

        return error_msg

    def _get_first_matching_attr(self, obj, *attrs, default=None):
        for attr in attrs:
            if hasattr(obj, attr):
                return getattr(obj, attr)

        return default


class CreateModelMixin:
    """
    Create a model instance.
    """

    def create(self, request, *_args, **_kwargs):
        request_serializer = self.get_request_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        instance = self.perform_create(request_serializer)

        response_serializer = self.get_response_serializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """

    def retrieve(self, _request, *_args, **_kwargs):
        instance = self.get_object()
        serializer = self.get_response_serializer(instance)
        return Response(serializer.data)


class ListModelMixin:
    """
    List a queryset.
    """

    def list(self, _request, *_args, **_kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_response_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_response_serializer(queryset, many=True)
        return Response(serializer.data)


class UpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *_args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request_serializer = self.get_request_serializer(
            instance, data=request.data, partial=partial
        )
        request_serializer.is_valid(raise_exception=True)

        instance = self.perform_update(instance, request_serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_response_serializer(instance)
        return Response(response_serializer.data)

    def perform_update(self, instance, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, *_args, **_kwargs):
        instance = self.get_object()
        serializer = self.get_request_serializer_or_none(instance, data=request.data)
        if serializer is not None:
            serializer.is_valid(raise_exception=True)
            self.perform_destroy(instance, serializer)
        else:
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, serializer=None):
        instance.delete()
