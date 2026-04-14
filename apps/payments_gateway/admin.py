from django.contrib import admin
from payments.models import BasePayment
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'variant', 'status', 'total', 'currency', 'created']
    list_filter = ['variant', 'status']
    search_fields = ['id', 'transaction_id']
    readonly_fields = ['created', 'modified']
