from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('items/', include('apps.items.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('contact/', include('apps.contact.urls')),
    path('payments_gateway/', include('apps.payments_gateway.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
