from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('cart/', views.booking_cart, name='cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:booking_number>/', views.booking_success, name='booking_success'),
]
