from django.core.management.base import BaseCommand
from apps.items.models import HireItem

class Command(BaseCommand):
    help = 'Migrate old pricing to new simplified model'

    def handle(self, *args, **options):
        items = HireItem.objects.all()

        for item in items:
            # Determine pricing type based on existing data
            if item.price_per_period and item.price_per_period > 0:
                item.price = item.price_per_period
                item.pricing_type = 'period'
            elif item.price_per_day and item.price_per_day > 0:
                item.price = item.price_per_day
                item.pricing_type = 'day'
            else:
                item.price = 0
                item.pricing_type = 'period'

            item.save()
            self.stdout.write(f'Updated: {item.name} - {item.get_price_display()}')

        self.stdout.write(self.style.SUCCESS('Pricing migration complete!'))
