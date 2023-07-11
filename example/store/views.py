from rest_framework.decorators import action
from rest_framework.response import Response

from rest_batteries.mixins import CreateModelMixin, ListModelMixin
from rest_batteries.viewsets import GenericViewSet

from .models import Order
from .serializers import OrderCreateSerializer, OrderResponseSerializer
from .services import cancel_order, create_order


class OrderViewSet(
    CreateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related('lines__product')
    request_action_serializer_classes = {
        'create': OrderCreateSerializer,
    }
    response_action_serializer_classes = {
        'create': OrderResponseSerializer,
        'list': OrderResponseSerializer,
        'cancel': OrderResponseSerializer,
    }

    def perform_create(self, serializer):
        return create_order(**serializer.validated_data)

    @action(detail=True, methods=['post'])
    def cancel(self, _request, *_args, **_kwargs):
        order = self.get_object()
        order = cancel_order(order=order)

        response_serializer = self.get_response_serializer(order)
        return Response(response_serializer.data)
