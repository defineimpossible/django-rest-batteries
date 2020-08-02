from django.core.validators import MinValueValidator
from django.db import models

from .choices import OrderStatus


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)


class Order(models.Model):
    status = models.PositiveIntegerField(
        choices=OrderStatus.choices, default=OrderStatus.DRAFT
    )

    @property
    def total_price(self):
        return sum(line.product.price * line.quantity for line in self.lines.all())


class OrderLine(models.Model):
    order = models.ForeignKey('Order', related_name='lines', on_delete=models.CASCADE)
    product = models.ForeignKey(
        'Product', related_name='order_lines', on_delete=models.CASCADE
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('order', 'product')
