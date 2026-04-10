import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from apps.items.models import HireItem
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import time

'''
# Check/Confirm fixtures all loaded

python manage.py shell << 'EOF'
from apps.items.models import HireItem

items_with_images = HireItem.objects.exclude(image='')
items_without = HireItem.objects.filter(image='')

print(f"Items with images: {items_with_images.count()}")
for item in items_with_images:
    print(f"  ✓ {item.name}")

print(f"\nItems without images: {items_without.count()}")
for item in items_without:
    print(f"  ✗ {item.name}")
EOF
'''

class Command(BaseCommand):
    help = 'Load images for all hire items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download even if image exists',
        )
        parser.add_argument(
            '--placeholder',
            action='store_true',
            help='Use placeholder images instead of downloading',
        )

    def handle(self, *args, **options):
        force = options['force']
        use_placeholder = options['placeholder']

        # Create directory for images
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'items'), exist_ok=True)

        # Define reliable image URLs for each item
        item_images = {
            'romantic-rose-backdrop': {
                'url': 'https://picsum.photos/id/29/800/600',  # Beautiful flower
                'alt': 'Romantic rose backdrop'
            },
            'gold-chiavari-chairs': {
                'url': 'https://picsum.photos/id/30/800/600',  # Elegant chair
                'alt': 'Gold chiavari chairs'
            },
            'led-uplighting-package': {
                'url': 'https://picsum.photos/id/31/800/600',  # Lighting effect
                'alt': 'LED uplighting'
            },
            'led-uplights': {
                'url': 'https://picsum.photos/id/31/800/600',  # Lighting effect
                'alt': 'LED uplights'
            },
            'floral-centerpiece': {
                'url': 'https://picsum.photos/id/28/800/600',  # Flowers
                'alt': 'Floral centerpiece'
            },
            'bohemian-backdrop': {
                'url': 'https://picsum.photos/id/15/800/600',  # Nature texture
                'alt': 'Bohemian backdrop'
            },
            'bohemian-macrame-backdrop': {
                'url': 'https://picsum.photos/id/15/800/600',  # Nature texture
                'alt': 'Bohemian macrame backdrop'
            },
            'cocktail-tables': {
                'url': 'https://picsum.photos/id/20/800/600',  # Table setting
                'alt': 'Cocktail tables'
            },
            'cocktail-table-set': {
                'url': 'https://picsum.photos/id/20/800/600',  # Table setting
                'alt': 'Cocktail table set'
            },
            'fairy-light-curtain': {
                'url': 'https://picsum.photos/id/26/800/600',  # Lights
                'alt': 'Fairy light curtain'
            },
            'balloon-arch-kit': {
                'url': 'https://picsum.photos/id/27/800/600',  # Colorful
                'alt': 'Balloon arch kit'
            },
            'neon-sign-love': {
                'url': 'https://picsum.photos/id/32/800/600',  # Neon effect
                'alt': 'Neon sign'
            },
            'velvet-lounge-suite': {
                'url': 'https://picsum.photos/id/16/800/600',  # Luxury furniture
                'alt': 'Velvet lounge suite'
            },
            'velvet-lounge': {
                'url': 'https://picsum.photos/id/16/800/600',  # Luxury furniture
                'alt': 'Velvet lounge'
            },
            'white-tablecloths': {
                'url': 'https://picsum.photos/id/18/800/600',  # Table setting
                'alt': 'White tablecloths'
            },
            'premium-white-tablecloths-10-pack': {
                'url': 'https://picsum.photos/id/18/800/600',  # Table setting
                'alt': 'Premium white tablecloths'
            },
            'geometric-centerpiece': {
                'url': 'https://picsum.photos/id/21/800/600',  # Geometric design
                'alt': 'Geometric centerpiece'
            },
            'rose-gold-backdrop': {
                'url': 'https://picsum.photos/id/29/800/600',  # Flower
                'alt': 'Rose gold backdrop'
            },
            'chiavari-chairs': {
                'url': 'https://picsum.photos/id/30/800/600',  # Chair
                'alt': 'Chiavari chairs'
            },
        }

        self.stdout.write('Loading images for items...\n')

        # Get all items
        items = HireItem.objects.all()
        self.stdout.write(f'Found {items.count()} items in database\n')

        success_count = 0
        skip_count = 0
        fail_count = 0

        for item in items:
            # Skip if image already exists and not forcing
            if item.image and not force:
                self.stdout.write(self.style.WARNING(f'⏭️  Skipping {item.name} (image already exists)'))
                skip_count += 1
                continue

            # Try to get image URL for this item
            image_info = None
            for slug_pattern, info in item_images.items():
                if slug_pattern in item.slug or item.slug.startswith(slug_pattern):
                    image_info = info
                    break

            if use_placeholder:
                # Create placeholder image
                success = self.create_placeholder_image(item)
            else:
                # Download image
                success = self.download_image(item, image_info)

            if success:
                self.stdout.write(self.style.SUCCESS(f'✓ Added image to: {item.name}'))
                success_count += 1
            else:
                # Fallback to placeholder if download fails
                self.stdout.write(self.style.WARNING(f'⚠️  Download failed for {item.name}, creating placeholder...'))
                if self.create_placeholder_image(item):
                    self.stdout.write(self.style.SUCCESS(f'✓ Created placeholder for: {item.name}'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Failed to add image to: {item.name}'))
                    fail_count += 1

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Image Loading Complete!'))
        self.stdout.write(f'  Success: {success_count}')
        self.stdout.write(f'  Skipped: {skip_count}')
        self.stdout.write(f'  Failed: {fail_count}')
        self.stdout.write('='*50)

        # Show items with and without images
        items_with_images = HireItem.objects.exclude(image='')
        items_without_images = HireItem.objects.filter(image='')

        self.stdout.write(f'\n📸 Items with images: {items_with_images.count()}')
        for item in items_with_images[:10]:
            self.stdout.write(f'  • {item.name}')

        if items_without_images.exists():
            self.stdout.write(f'\n⚠️  Items still missing images: {items_without_images.count()}')
            for item in items_without_images:
                self.stdout.write(f'  • {item.name}')

    def download_image(self, item, image_info):
        """Download image from URL"""
        try:
            # Use a default URL if no specific one found
            if not image_info:
                image_url = f'https://picsum.photos/id/{hash(item.name) % 100}/800/600'
            else:
                image_url = image_info['url']

            # Download image
            response = requests.get(image_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                # Create filename
                filename = f"items/{item.slug}.jpg"

                # Save image
                image_content = ContentFile(response.content)
                item.image.save(filename, image_content, save=True)
                return True
            else:
                self.stdout.write(f'    HTTP {response.status_code} for {item.name}')
                return False

        except requests.RequestException as e:
            self.stdout.write(f'    Request error for {item.name}: {str(e)[:50]}')
            return False
        except Exception as e:
            self.stdout.write(f'    Error for {item.name}: {str(e)[:50]}')
            return False

    def create_placeholder_image(self, item):
        """Create a colored placeholder image with text"""
        try:
            # Create image
            img = Image.new('RGB', (800, 600), color=self.get_color_for_item(item))
            draw = ImageDraw.Draw(img)

            # Try to load a font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                except:
                    font = ImageFont.load_default()

            # Add text
            text = item.name[:30]
            from PIL import ImageFont, ImageDraw

            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            position = ((800 - text_width) // 2, (600 - text_height) // 2)
            draw.text(position, text, fill='white', font=font)

            # Add category text
            category_text = f"Category: {item.category.name}"
            bbox2 = draw.textbbox((0, 0), category_text, font=font)
            cat_width = bbox2[2] - bbox2[0]
            position2 = ((800 - cat_width) // 2, (600 - text_height) // 2 + 60)
            draw.text(position2, category_text, fill='white', font=font)

            # Save to bytes
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)

            # Save to model
            filename = f"items/{item.slug}_placeholder.jpg"
            item.image.save(filename, ContentFile(img_byte_arr.getvalue()), save=True)
            return True

        except Exception as e:
            self.stdout.write(f'    Placeholder error: {str(e)}')
            return False

    def get_color_for_item(self, item):
        """Generate a color based on item category"""
        colors = {
            'flower': '#FF69B4',  # Pink
            'backdrop': '#9B59B6',  # Purple
            'furniture': '#2C3E50',  # Dark Blue
            'lighting': '#F39C12',  # Orange
            'tableware': '#27AE60',  # Green
            'party': '#E74C3C',  # Red
        }

        category_name = item.category.name.lower()
        for key, color in colors.items():
            if key in category_name:
                return color
        return '#3498DB'  # Default blue


