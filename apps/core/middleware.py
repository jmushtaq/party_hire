from django.utils.deprecation import MiddlewareMixin

class ThemeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get theme from session or GET parameter
        theme = request.GET.get('theme')
        if theme:
            request.session['active_theme'] = theme
        elif 'active_theme' not in request.session:
            request.session['active_theme'] = 'default'

        # Make theme available in request
        request.active_theme = request.session.get('active_theme', 'default')

class ThemeContextMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            response.context_data['active_theme'] = getattr(request, 'active_theme', 'default')
            response.context_data['available_themes'] = request.session.get('available_themes', {})
        return response
