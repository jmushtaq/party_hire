from django.conf import settings

def theme_context(request):
    """Add theme context to all templates"""
    theme = request.GET.get('theme')
    if theme and theme in settings.AVAILABLE_THEMES:
        request.session['active_theme'] = theme
    elif 'active_theme' not in request.session:
        request.session['active_theme'] = getattr(settings, 'ACTIVE_THEME', 'default')

    active_theme = request.session.get('active_theme', 'default')

    return {
        'active_theme': active_theme,
        'available_themes': settings.AVAILABLE_THEMES,
    }

def cart_count_context(request):
    """Add cart count to all templates"""
    cart = request.session.get('booking_cart', {})
    return {
        'cart_count': len(cart)
    }

def date_range_context(request):
    """Add date range to all templates"""
    start_date = request.session.get('booking_start_date')
    end_date = request.session.get('booking_end_date')

    # Determine if we should show the date picker
    # Show on all pages except checkout and payment
    path = request.path
    show_picker = not any(x in path for x in ['checkout', 'payment', 'success'])

    return {
        'show_date_picker': show_picker,
        'booking_start_date': start_date,
        'booking_end_date': end_date,
    }

def party_hire_url(request):
    return {
        'DJANGO_SETTINGS': settings,
        'DEBUG': settings.DEBUG,
        'SYSTEM_NAME_SHORT': settings.SYSTEM_NAME_SHORT,
        'SYSTEM_NAME': settings.SYSTEM_NAME,
        'PUBLIC_URL': settings.PUBLIC_URL,
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
        'DEPOSIT': int(settings.DEPOSIT * 100),
        #'build_tag': settings.BUILD_TAG,
    }
