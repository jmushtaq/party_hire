
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
    list_display = ['name', 'category', 'price', 'pricing_type', 'quantity_available', 'is_available', 'featured']
    list_filter = ['category', 'pricing_type', 'is_available', 'featured']
    search_fields = ['name', 'description']
    inlines = [ItemAvailabilityInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'pricing_type', 'deposit_percentage'),
            'description': 'Select how this item is priced - per period (Thu-Mon), per day, or per week'
        }),
        ('Inventory', {
            'fields': ('quantity_available', 'is_available', 'featured')
        }),
        ('Media', {
            'fields': ('image', 'gallery_images')
        }),
        ('Specifications', {
            'fields': ('dimensions', 'weight'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ItemAvailability)
class ItemAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['item', 'date', 'is_booked', 'quantity_booked']
    list_filter = ['item', 'date']
