[![Build Status](https://travis-ci.org/defineimpossible/django-rest-batteries.svg?branch=master)](https://travis-ci.org/github/defineimpossible/django-rest-batteries)
[![Coverage](https://codecov.io/gh/defineimpossible/django-rest-batteries/branch/master/graph/badge.svg)](https://codecov.io/gh/defineimpossible/django-rest-batteries)

# Django REST Framework Batteries

Build clean APIs with DRF faster.

# Overview

Here's a quick overview of what the library has at the moment:

- Action-based serializers for ViewSets
- Two serializers per request/response cycle for ViewSets and GenericAPIViews
- Action-based permissions for ViewSets
- Single format for all errors

# Requirements

- Python ≥ 3.6
- Django (2.2, 3.0)
- Django REST Framework (3.9, 3.10, 3.11)

# Installation

```bash
$ pip install django-rest-batteries
```

# Usage

## Action-based serializers for ViewSets

Each action can have a separate serializer:

```python
from rest_batteries.mixins import RetrieveModelMixin, ListModelMixin
from rest_batteries.viewsets import GenericViewSet
...

class OrderViewSet(RetrieveModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    response_action_serializer_classes = {
        'retrieve': OrderSerializer,
        'list': OrderListSerializer,
    }
```

## Two serializers per request/response cycle

We found that more often than not we need a separate serializer for handling request payload and a separate serializer for generating response data.

How to achieve it in ViewSet:

```python
from rest_batteries.mixins import CreateModelMixin, ListModelMixin
from rest_batteries.viewsets import GenericViewSet
...

class OrderViewSet(CreateModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    request_action_serializer_classes = {
        'create': OrderCreateSerializer,
    }
    response_action_serializer_classes = {
        'create': OrderResponseSerializer,
        'list': OrderResponseSerializer,
        'cancel': OrderResponseSerializer,
    }
```

How to achieve it in GenericAPIView:

```python
from rest_batteries.generics import CreateAPIView
...


class OrderCreateView(CreateAPIView):
    request_serializer_class = OrderCreateSerializer
    response_serializer_class = OrderResponseSerializer
```

## Action-based permissions for ViewSets

Each action can have a separate set of permissions:

```python
from rest_batteries.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin
from rest_batteries.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
...

class OrderViewSet(CreateModelMixin,
                   UpdateModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    action_permission_classes = {
        'create': IsAuthenticated,
        'update': [IsAuthenticated, IsOrderOwner],
        'list': AllowAny,
    }
```

## Single format for all errors

We believe that having a single format for all errors is good practice. This will make the process of displaying and handling errors much simpler for clients that use your APIs.

Any error always will be a JSON object with a message, code (identifier of the error), and field if the error is specific to a particular field. How your response could look like:

```python
{
    "errors": [
        {
            "message": "Delete or cancel all reservations first.",
            "code": "invalid"
        },
        {
            "message": "Ensure this field has no more than 21 characters.",
            "code": "max_length",
            "field": "address.work_phone"
        },
        {
            "message": "This email already exists",
            "code": "unique",
            "field": "login_email"
        }
    ]
}
```

You will not have a single format out-of-the-box after installation. You need to add an exception handler to your DRF settings:

```python
REST_FRAMEWORK = {
    ...
    'EXCEPTION_HANDLER': 'rest_batteries.exception_handlers.errors_formatter_exception_handler',
}
```

# Credits

- [Django-Styleguide by HackSoftware](https://github.com/HackSoftware/Django-Styleguide) - inspiration
