from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class HireItem(models.Model):
    PRICING_CHOICES = [
        ('period', 'Per Hire Period (Thu-Mon)'),
        ('day', 'Per Day'),
        ('week', 'Per Week'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()

    # Simplified pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Base price")
    pricing_type = models.CharField(max_length=10, choices=PRICING_CHOICES, default='period',
                                    help_text="How this item is priced")

    deposit_percentage = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    image = models.ImageField(upload_to='items/')
    gallery_images = models.JSONField(default=list, blank=True)
    quantity_available = models.IntegerField(default=1)
    dimensions = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_price_display(self):
        """Return formatted price with period type"""
        from decimal import Decimal
        price_formatted = f"${self.price:,.2f}"
        if self.pricing_type == 'period':
            return f"{price_formatted}/period"
        elif self.pricing_type == 'day':
            return f"{price_formatted}/day"
        else:
            return f"{price_formatted}/week"

    def get_price_label(self):
        """Return just the label (e.g., 'per period')"""
        return dict(self.PRICING_CHOICES).get(self.pricing_type, 'per period').lower()

    def calculate_total_price(self, quantity, start_date, end_date):
        """Calculate total price based on pricing type and date range"""
        from decimal import Decimal

        # Ensure we're working with Decimal types
        days = (end_date - start_date).days + 1
        quantity_decimal = Decimal(str(quantity))
        price_decimal = Decimal(str(self.price))

        if self.pricing_type == 'period':
            # Standard period is 4 days (Thu-Mon)
            periods = max(Decimal('1'), Decimal(str(days)) / Decimal('4'))
            return price_decimal * quantity_decimal * periods
        elif self.pricing_type == 'day':
            return price_decimal * quantity_decimal * Decimal(str(days))
        else:  # week
            weeks = max(Decimal('1'), Decimal(str(days)) / Decimal('7'))
            return price_decimal * quantity_decimal * weeks

    def calculate_deposit(self, total_amount):
        return (self.deposit_percentage / 100) * total_amount

class ItemAvailability(models.Model):
    item = models.ForeignKey(HireItem, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
    quantity_booked = models.IntegerField(default=0)

    class Meta:
        unique_together = ['item', 'date']
        ordering = ['date']

    def __str__(self):
        return f"{self.item.name} - {self.date}"
