from rest_framework import serializers

from ..models import Order, OrderLine, Product


class ProductResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
        )


class OrderLineResponseSerializer(serializers.ModelSerializer):
    product = ProductResponseSerializer()

    class Meta:
        model = OrderLine
        fields = (
            'id',
            'product',
            'quantity',
        )


class OrderResponseSerializer(serializers.ModelSerializer):
    lines = OrderLineResponseSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'total_price',
            'lines',
        )
