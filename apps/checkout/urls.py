from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('process/<int:payment_id>/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]
