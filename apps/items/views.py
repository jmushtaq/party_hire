from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, HireItem

class ItemListView(ListView):
    model = HireItem
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        queryset = HireItem.objects.filter(is_available=True)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # Add breadcrumbs
        if hasattr(self, 'category'):
            context['breadcrumbs'] = [
                {'name': 'All Items', 'url': '/items/', 'icon': 'fas fa-gift'},
                {'name': self.category.name, 'url': '', 'icon': 'fas fa-tag'}
            ]
        else:
            context['breadcrumbs'] = [
                {'name': 'All Items', 'url': '', 'icon': 'fas fa-gift'}
            ]

        return context

class ItemDetailView(DetailView):
    model = HireItem
    template_name = 'items/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unavailable dates for this item
        unavailable_dates = self.object.availability.filter(is_booked=True).values_list('date', flat=True)
        context['unavailable_dates'] = list(unavailable_dates)

        # Add breadcrumb for this item
        context['breadcrumbs'] = [
            {'name': 'All Items', 'url': '/items/', 'icon': 'fas fa-gift'},
            {'name': self.object.name, 'url': '', 'icon': 'fas fa-box'}
        ]

        return context

