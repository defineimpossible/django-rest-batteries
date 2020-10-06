import pytest
from django.core.exceptions import ValidationError
from django.urls import path
from rest_batteries.errors_formatter import ErrorsFormatter
from rest_batteries.views import APIView
from rest_framework import serializers
from rest_framework.views import exception_handler as drf_exception_handler

from .models import Article


class APIViewRaisesValueError(APIView):
    def post(self, _request, *_args, **_kwargs):
        raise ValueError('Value error raised')


class APIViewRaisesDjangoValidationError(APIView):
    def post(self, _request, *_args, **_kwargs):
        raise ValidationError('Django validation error raised')


class APIViewRaisesDjangoFieldValidationError(APIView):
    def post(self, _request, *_args, **_kwargs):
        article = Article(title='t' * 500, text='text')
        article.full_clean()
        article.save()


class APIViewRaisesObjectFieldValidationError(APIView):
    def post(self, _request, *_args, **_kwargs):
        class ChildSerializer(serializers.Serializer):
            text = serializers.CharField()

        class ParentSerializer(serializers.Serializer):
            child = ChildSerializer()

        serializer = ParentSerializer(data={'child': {'text': False}})
        serializer.is_valid(raise_exception=True)


class APIViewRaisesArrayFieldValidationError(APIView):
    def post(self, _request, *_args, **_kwargs):
        class ChildSerializer(serializers.Serializer):
            text = serializers.CharField()

        class ParentSerializer(serializers.Serializer):
            children = ChildSerializer(many=True)

        serializer = ParentSerializer(
            data={
                'children': [{'text': 'comment-text'}, {'text': False}, {'text': False}]
            }
        )
        serializer.is_valid(raise_exception=True)


urlpatterns = [
    path('django-validation-error/', APIViewRaisesDjangoValidationError.as_view()),
    path(
        'django-field-validation-error/',
        APIViewRaisesDjangoFieldValidationError.as_view(),
    ),
    path(
        'object-field-validation-error/',
        APIViewRaisesObjectFieldValidationError.as_view(),
    ),
    path(
        'array-field-validation-error/',
        APIViewRaisesArrayFieldValidationError.as_view(),
    ),
]


@pytest.fixture(autouse=True)
def root_urlconf(settings):
    settings.ROOT_URLCONF = __name__


@pytest.fixture
def exception_handler(settings):
    settings.REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'rest_batteries.exception_handlers.errors_formatter_exception_handler'
    }


@pytest.fixture
def custom_exception_handler(settings):
    class CustomErrorsFormatter(ErrorsFormatter):
        def get_field_name(self, field_name):
            return 'custom_' + field_name

    def _handler(exc, context):
        response = drf_exception_handler(exc, context)

        if response is None:
            return response

        formatter = CustomErrorsFormatter(exc)

        response.data = formatter()

        return response

    settings.REST_FRAMEWORK = {'EXCEPTION_HANDLER': _handler}


class TestAPIViewErrors:
    def test_django_validation_error_transforms_into_drf_validation_error(
        self, api_client
    ):
        response = api_client.post('/django-validation-error/')
        assert response.status_code == 400
        assert response.data == ['Django validation error raised']

    def test_django_validation_error_transforms_into_drf_validation_error__when_field_error(
        self, api_client
    ):
        response = api_client.post('/django-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'title': ['Ensure this value has at most 255 characters (it has 500).']
        }


@pytest.mark.usefixtures('exception_handler')
class TestAPIViewErrorsFormat:
    def test_validation_error(self, api_client):
        response = api_client.post('/django-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [{'code': 'invalid', 'message': 'Django validation error raised'}]
        }

    def test_field_validation_error(self, api_client):
        response = api_client.post('/django-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [
                {
                    'code': 'max_length',
                    'message': 'Ensure this value has at most 255 characters (it has 500).',
                    'field': 'title',
                }
            ]
        }

    def test_object_field_validation_error(self, api_client):
        response = api_client.post('/object-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'child.text',
                }
            ]
        }

    def test_array_field_validation_error(self, api_client):
        response = api_client.post('/array-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'children[1].text',
                },
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'children[2].text',
                },
            ]
        }


@pytest.mark.usefixtures('custom_exception_handler')
class TestAPIViewCustomErrorsFormat:
    def test_object_field_validation_error(self, api_client):
        response = api_client.post('/object-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'custom_child.custom_text',
                }
            ]
        }

    def test_array_field_validation_error(self, api_client):
        response = api_client.post('/array-field-validation-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'custom_children[1].custom_text',
                },
                {
                    'code': 'invalid',
                    'message': 'Not a valid string.',
                    'field': 'custom_children[2].custom_text',
                },
            ]
        }
