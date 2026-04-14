from django.db import models
from payments.models import BasePayment

class Payment(BasePayment):
    """Custom payment model for party hire"""

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
