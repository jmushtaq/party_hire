from django.conf import settings

def theme_context(request):
    return {
        'active_theme': getattr(settings, 'ACTIVE_THEME', 'default'),
        'available_themes': getattr(settings, 'AVAILABLE_THEMES', ['default']),
    }
