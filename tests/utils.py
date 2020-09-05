from unittest import mock

from rest_framework.test import APIClient as DRFClient


class APIClient(DRFClient):
    def login(
        self,
        user=None,
        backend='django.contrib.auth.backends.ModelBackend',
        **credentials
    ):
        if user is None:
            return super().login(**credentials)

        with mock.patch('django.contrib.auth.authenticate') as authenticate:
            user.backend = backend
            authenticate.return_value = user
            return super().login(**credentials)
