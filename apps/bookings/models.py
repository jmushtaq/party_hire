from django.db import models
from django.conf import settings
from apps.items.models import HireItem
from decimal import Decimal

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('deposit_paid', 'Deposit Paid'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    booking_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()

    start_date = models.DateField()
    end_date = models.DateField()

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_number:
            import uuid
            self.booking_number = f"BK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        total = self.subtotal + self.delivery_cost
        self.total_amount = total
        self.deposit_amount = total * Decimal(settings.DEPOSIT)
        return total

    def __str__(self):
        return f"{self.booking_number} - {self.customer_name}"

class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(HireItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_days = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.price_per_day * self.quantity * self.number_of_days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} x{self.quantity}"
