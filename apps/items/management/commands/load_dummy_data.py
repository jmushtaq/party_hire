from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.files import File
from apps.items.models import Category, HireItem, ItemAvailability
from datetime import datetime, timedelta
import json
import os

'''
# Check/Confirm images all loaded

python manage.py shell << 'EOF'
from apps.items.models import Category, HireItem
from datetime import datetime, timedelta

print("Adding demo data...")

# Create categories (using get_or_create to handle existing data)
categories_data = [
    ('Flower Arrangements', 'flower-arrangements', 'Beautiful fresh and artificial flowers for all occasions. From elegant bouquets to grand centerpieces.'),
    ('Backdrops & Walls', 'backdrops-walls', 'Create stunning photo opportunities with our range of backdrops, flower walls, and geometric decor.'),
    ('Furniture', 'furniture', 'Elegant furniture for any event including chiavari chairs, lounges, bar stools, and tables.'),
    ('Lighting & Effects', 'lighting-effects', 'Create the perfect atmosphere with our lighting solutions including uplighting, festoon lights, and special effects.'),
    ('Tableware & Decor', 'tableware-decor', 'Complete your tablescape with our range of tablecloths, runners, centerpieces, and tableware.'),
    ('Party Accessories', 'party-accessories', 'Everything you need for a memorable party including balloons, signs, and party favors.'),
]

categories = {}
for name, slug, desc in categories_data:
    cat, created = Category.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'description': desc
        }
    )
    categories[slug] = cat
    print(f'  {"Created" if created else "Found"} category: {name}')

# Create sample items
items_data = [
    # name, slug, category_slug, description, price_per_day, featured, quantity
    ('Rose Gold Backdrop', 'rose-gold-backdrop', 'backdrops-walls',
     'Stunning 8ft x 8ft rose gold sequin backdrop. Perfect for photos, weddings, and special events. Creates a glamorous shimmering effect.',
     299.00, True, 3),

    ('Chiavari Chairs (Set of 10)', 'chiavari-chairs', 'furniture',
     'Elegant gold resin chiavari chairs with cushioned seats. Set includes 10 chairs. Perfect for weddings, galas, and formal events.',
     150.00, True, 50),

    ('LED Uplights (8 Pack)', 'led-uplights', 'lighting-effects',
     'Wireless LED uplights that can be set to any color. Perfect for creating ambiance at weddings, corporate events, and parties. Includes remote control.',
     199.00, True, 20),

    ('Elegant Floral Centerpiece', 'floral-centerpiece', 'flower-arrangements',
     'Stunning fresh flower centerpiece featuring roses, hydrangeas, and eucalyptus. Customizable colors to match your theme.',
     85.00, False, 15),

    ('Bohemian Macrame Backdrop', 'boho-backdrop', 'backdrops-walls',
     'Beautiful boho-chic backdrop featuring macrame, pampas grass, and wooden beads. Perfect for bridal showers and casual weddings.',
     249.00, True, 2),

    ('Cocktail Tables (Set of 4)', 'cocktail-tables', 'furniture',
     'Set of 4 high cocktail tables with black linen. Perfect for mingling areas and cocktail hours. Each table stands 42" high.',
     120.00, False, 25),

    ('Fairy Light Curtain', 'fairy-light-curtain', 'lighting-effects',
     'Magical 10ft x 10ft fairy light curtain with warm white LED lights. Perfect for photo backdrops and stages.',
     149.00, False, 10),

    ('Balloon Arch Kit', 'balloon-arch-kit', 'party-accessories',
     'Complete balloon arch kit including frame, 100 balloons in your choice of colors, and assembly instructions. Creates a stunning 10ft arch.',
     199.00, True, 8),

    ('Neon Sign - LOVE', 'neon-sign-love', 'lighting-effects',
     'Eye-catching LED neon sign spelling LOVE. Great for photo walls and dance floors. Battery operated or plug-in.',
     129.00, True, 5),

    ('Velvet Lounge Suite', 'velvet-lounge', 'furniture',
     'Elegant velvet lounge suite including 2 sofas and 2 armchairs in emerald green. Perfect for VIP areas and sophisticated events.',
     399.00, True, 4),

    ('Premium White Tablecloths (10 Pack)', 'white-tablecloths', 'tableware-decor',
     'Set of 10 premium polyester tablecloths in crisp white. Wrinkle-resistant and machine washable. Fits standard 6ft and 8ft tables.',
     89.00, False, 100),

    ('Geometric Gold Centerpiece', 'geometric-centerpiece', 'tableware-decor',
     'Modern geometric gold terrarium centerpiece. Perfect for contemporary weddings and corporate events.',
     45.00, False, 30),
]

for name, slug, cat_slug, desc, price, featured, qty in items_data:
    category = categories.get(cat_slug)
    if category:
        item, created = HireItem.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'category': category,
                'description': desc,
                'price_per_day': price,
                'deposit_percentage': 10,
                'quantity_available': qty,
                'is_available': True,
                'featured': featured
            }
        )
        print(f'  {"Created" if created else "Found"} item: {name}')
    else:
        print(f'  ERROR: Category {cat_slug} not found for item {name}')

print(f"\n✅ Summary:")
print(f"  Categories: {Category.objects.count()}")
print(f"  Items: {HireItem.objects.count()}")
print(f"  Featured Items: {HireItem.objects.filter(featured=True).count()}")

# Show some sample items
print("\n📦 Sample Items Available:")
for item in HireItem.objects.filter(featured=True)[:5]:
    print(f"  • {item.name} - ${item.price_per_day}/day")
EOF
'''

class Command(BaseCommand):
    help = 'Load dummy data for party hire application'

    def handle(self, *args, **options):
        self.stdout.write('Loading dummy data...')

        # Load fixtures
        try:
            call_command('loaddata', 'apps/fixtures/categories.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Categories loaded'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Categories already exist or error: {e}'))

        try:
            call_command('loaddata', 'apps/fixtures/items.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Items loaded'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Items already exist or error: {e}'))

        # Create availability for next 90 days
        self.stdout.write('Creating availability calendar...')
        today = datetime.now().date()

        for item in HireItem.objects.all():
            created_count = 0
            for i in range(90):
                date = today + timedelta(days=i)
                availability, created = ItemAvailability.objects.get_or_create(
                    item=item,
                    date=date,
                    defaults={
                        'is_booked': False,
                        'quantity_booked': 0
                    }
                )
                if created:
                    created_count += 1
            self.stdout.write(f'  - {item.name}: {created_count} availability records')

        self.stdout.write(self.style.SUCCESS('\n✅ Dummy data loaded successfully!'))
        self.stdout.write(f'\nTotal Categories: {Category.objects.count()}')
        self.stdout.write(f'Total Items: {HireItem.objects.count()}')
        self.stdout.write(f'Total Availability Records: {ItemAvailability.objects.count()}')

