from django.contrib import admin
from .models import Category, HireItem, ItemAvailability

class ItemAvailabilityInline(admin.TabularInline):
    model = ItemAvailability
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug']

@admin.register(HireItem)
class HireItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'category', 'price_per_day', 'quantity_available', 'is_available', 'featured']
    list_filter = ['category', 'is_available', 'featured']
    search_fields = ['name', 'description']
    inlines = [ItemAvailabilityInline]

@admin.register(ItemAvailability)
class ItemAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['item', 'date', 'is_booked', 'quantity_booked']
    list_filter = ['item', 'date']
