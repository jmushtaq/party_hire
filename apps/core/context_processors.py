from django.conf import settings

def theme_context(request):
    # Get theme from session or GET parameter
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
