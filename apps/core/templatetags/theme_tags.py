from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('core/theme_switcher.html', takes_context=True)
def theme_switcher(context):
    request = context.get('request')
    current_theme = getattr(request, 'active_theme', 'default') if request else 'default'
    return {
        'themes': settings.AVAILABLE_THEMES,
        'current_theme': current_theme,
        'request': request
    }

@register.simple_tag(takes_context=True)
def get_theme_css(context):
    """Get the current theme's CSS file path"""
    request = context.get('request')
    if request and hasattr(request, 'active_theme'):
        theme = request.active_theme
    else:
        theme = getattr(settings, 'ACTIVE_THEME', 'default')

    theme_config = settings.AVAILABLE_THEMES.get(theme, {})
    css_file = theme_config.get('css_file', 'css/themes/default/style.css')
    return f"/static/{css_file}"
