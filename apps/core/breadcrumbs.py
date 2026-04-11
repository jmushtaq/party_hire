from django.urls import resolve
from django.utils.functional import SimpleLazyObject

def get_breadcrumbs(request):
    """Generate breadcrumbs based on current URL path"""
    path = request.path
    breadcrumbs = []

    # Home is always first (handled in template)

    # Items section
    if path.startswith('/items/'):
        if path == '/items/':
            breadcrumbs.append({
                'name': 'All Items',
                'url': '/items/',
                'icon': 'fas fa-gift'
            })
        elif '/category/' in path:
            # Extract category slug from path
            parts = path.split('/')
            if len(parts) > 3:
                category_slug = parts[3]
                breadcrumbs.append({
                    'name': 'All Items',
                    'url': '/items/',
                    'icon': 'fas fa-gift'
                })
                breadcrumbs.append({
                    'name': category_slug.replace('-', ' ').title(),
                    'url': path,
                    'icon': 'fas fa-tag'
                })
        else:
            # Item detail page
            breadcrumbs.append({
                'name': 'All Items',
                'url': '/items/',
                'icon': 'fas fa-gift'
            })

    # Bookings section
    elif path.startswith('/bookings/'):
        if 'cart' in path:
            breadcrumbs.append({
                'name': 'Shopping Cart',
                'url': '/bookings/cart/',
                'icon': 'fas fa-shopping-cart'
            })
        elif 'checkout' in path:
            breadcrumbs.append({
                'name': 'Shopping Cart',
                'url': '/bookings/cart/',
                'icon': 'fas fa-shopping-cart'
            })
            breadcrumbs.append({
                'name': 'Checkout',
                'url': '/bookings/checkout/',
                'icon': 'fas fa-credit-card'
            })
        elif 'success' in path:
            breadcrumbs.append({
                'name': 'Shopping Cart',
                'url': '/bookings/cart/',
                'icon': 'fas fa-shopping-cart'
            })
            breadcrumbs.append({
                'name': 'Checkout',
                'url': '/bookings/checkout/',
                'icon': 'fas fa-credit-card'
            })
            breadcrumbs.append({
                'name': 'Booking Confirmed',
                'url': path,
                'icon': 'fas fa-check-circle'
            })

    # Contact section
    elif path.startswith('/contact/'):
        breadcrumbs.append({
            'name': 'Contact Us',
            'url': '/contact/',
            'icon': 'fas fa-envelope'
        })

    return breadcrumbs

def breadcrumbs_context(request):
    """Context processor to add breadcrumbs to all templates"""
    return {
        'breadcrumbs': get_breadcrumbs(request)
    }

