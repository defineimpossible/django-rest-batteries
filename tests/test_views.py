import pytest
from django.core.exceptions import ValidationError
from django.urls import path
from rest_batteries.views import APIView

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


urlpatterns = [
    path('value-error/', APIViewRaisesValueError.as_view()),
    path('django-validation-error/', APIViewRaisesDjangoValidationError.as_view()),
    path(
        'django-field-validation-error/',
        APIViewRaisesDjangoFieldValidationError.as_view(),
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


class TestAPIViewErrors:
    def test_value_error_transforms_into_drf_validation_error(self, api_client):
        response = api_client.post('/value-error/')
        assert response.status_code == 400
        assert response.data == ['Value error raised']

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
    def test_value_error(self, api_client):
        response = api_client.post('/value-error/')
        assert response.status_code == 400
        assert response.data == {
            'errors': [{'code': 'invalid', 'message': 'Value error raised'}]
        }

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
                    'code': 'invalid',
                    'message': 'Ensure this value has at most 255 characters (it has 500).',
                    'field': 'title',
                }
            ]
        }