from django import template
from apps.items.models import HireItem

register = template.Library()

@register.filter
def get_item_from_db(item_id):
    """Get hire item from database by ID"""
    try:
        return HireItem.objects.get(id=item_id)
    except HireItem.DoesNotExist:
        return None
