from django.contrib import admin

from .models import Order, OrderLine, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    pass
