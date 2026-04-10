from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item_list'),
    path('category/<slug:category_slug>/', views.ItemListView.as_view(), name='category_items'),
    path('<slug:slug>/', views.ItemDetailView.as_view(), name='item_detail'),
]
