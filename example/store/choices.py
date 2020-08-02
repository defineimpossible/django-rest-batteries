from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.IntegerChoices):
    DRAFT = 0, _('Draft')
    APPROVED = 1, _('Approved')
    DELIVERED = 2, _('Delivered')
    CANCELED = 3, _('Canceled')
