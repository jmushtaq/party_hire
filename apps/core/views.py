from django.views.generic import TemplateView
from apps.items.models import HireItem, Category

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_items'] = HireItem.objects.filter(featured=True, is_available=True)[:6]
        context['categories'] = Category.objects.all()
        return context
