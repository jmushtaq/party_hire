#!/usr/bin/env python
import os
import sys
import django
from django.core.management import call_command
from django.core.files import File
from django.conf import settings
import requests
from io import BytesIO

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'party_hire.settings')
django.setup()

from apps.items.models import Category, HireItem

def download_image(url, filename):
    """Download an image from URL and save to media directory"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Create directory if it doesn't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'items'), exist_ok=True)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'categories'), exist_ok=True)

            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def load_fixtures():
    """Load all fixture data"""
    print("Loading categories...")
    call_command('loaddata', 'categories.json', verbosity=1)

    print("Loading items...")
    call_command('loaddata', 'items.json', verbosity=1)

    print("Dummy data loaded successfully!")

def update_with_placeholder_images():
    """Update items with placeholder images"""
    # Placeholder image URLs (using placeholder images from placeholder service)
    placeholder_images = {
        1: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?w=400",  # Rose backdrop
        2: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400",  # Chiavari chairs
        3: "https://images.unsplash.com/photo-1519167758483-2a4a2f29b36d?w=400",  # Uplighting
        4: "https://images.unsplash.com/photo-1470004914212-05527e5e66d7?w=400",  # Centerpiece
        5: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?w=400",  # Boho backdrop
        6: "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400",  # Cocktail tables
        7: "https://images.unsplash.com/photo-1513151233558-860c539d3fa6?w=400",  # Fairy lights
        8: "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=400",  # Tablecloth
        9: "https://images.unsplash.com/photo-1470084347108-d6d8e9cffae6?w=400",  # Balloon arch
        10: "https://images.unsplash.com/photo-1470004914212-05527e5e66d7?w=400",  # Geometric centerpiece
        11: "https://images.unsplash.com/photo-1563089145-599997674d42?w=400",  # Neon sign
        12: "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400",  # Velvet lounge
    }

    for item_id, image_url in placeholder_images.items():
        try:
            item = HireItem.objects.get(pk=item_id)
            filename = f"items/item_{item_id}.jpg"
            if download_image(image_url, filename):
                item.image = filename
                item.save()
                print(f"Added image for {item.name}")
        except HireItem.DoesNotExist:
            print(f"Item {item_id} not found")

def generate_availability():
    """Generate availability for the next 90 days"""
    from datetime import datetime, timedelta
    from apps.items.models import ItemAvailability

    today = datetime.now().date()

    for item in HireItem.objects.all():
        # Create availability for next 90 days
        for i in range(90):
            date = today + timedelta(days=i)
            # Make some weekends booked for popular items
            is_booked = False
            if date.weekday() >= 5 and item.featured:  # Weekend and featured
                is_booked = i % 3 == 0  # Book every 3rd weekend

            ItemAvailability.objects.get_or_create(
                item=item,
                date=date,
                defaults={
                    'is_booked': is_booked,
                    'quantity_booked': 1 if is_booked else 0
                }
            )
        print(f"Created availability for {item.name}")

if __name__ == "__main__":
    print("=" * 50)
    print("Loading dummy data for Party Hire")
    print("=" * 50)

    # Load fixtures
    load_fixtures()

    # Add placeholder images (optional)
    print("\nAdding placeholder images...")
    update_with_placeholder_images()

    # Generate availability
    print("\nGenerating availability calendar...")
    generate_availability()

    print("\n✅ Dummy data loaded successfully!")
    print("\nYou can now:")
    print("  - Visit http://localhost:8000 to see the items")
    print("  - Browse categories and items")
    print("  - Test booking functionality")
