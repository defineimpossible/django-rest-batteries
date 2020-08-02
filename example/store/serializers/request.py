from rest_framework import serializers

from ..models import Product


class OrderLineSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )
    quantity = serializers.IntegerField()


class OrderCreateSerializer(serializers.Serializer):
    lines = OrderLineSerializer(many=True)
