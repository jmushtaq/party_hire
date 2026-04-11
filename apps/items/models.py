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
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    price_per_period = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Changed from price_per_day
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)  # Keep for backward compatibility
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

    def calculate_deposit(self, total_amount):
        return (self.deposit_percentage / 100) * total_amount

    def calculate_hire_period_days(self, pickup_date, return_date):
        """Calculate number of days for hire period (Thursday to Monday)"""
        # Standard hire period: Thursday 3pm to Monday 7pm = 4 days
        # But we'll calculate actual days
        return (return_date - pickup_date).days

    def get_price_for_period(self, pickup_date, return_date):
        """Calculate price based on hire period"""
        days = self.calculate_hire_period_days(pickup_date, return_date)
        return self.price_per_day * days

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
