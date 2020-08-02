from .choices import OrderStatus
from .models import Order, OrderLine, Product


def create_order(*, lines: dict) -> Order:
    order = Order.objects.create()
    for line in lines:
        create_order_line(order=order, **line)
    return order


def create_order_line(*, order: Order, product: Product, quantity: int) -> OrderLine:
    line = OrderLine(order=order, product=product, quantity=quantity)
    line.full_clean()
    line.save()
    return line


def cancel_order(*, order: Order) -> Order:
    order.status = OrderStatus.CANCELED
    order.save(update_fields=['status'])
    return order
