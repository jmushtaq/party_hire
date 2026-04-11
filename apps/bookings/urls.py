from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('cart/', views.booking_cart, name='cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:booking_number>/', views.booking_success, name='booking_success'),
]
