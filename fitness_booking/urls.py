"""
URL configuration for fitness_booking project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booking_api.urls')),
    # Redirect root URL to API endpoints
    path('', RedirectView.as_view(url='/api/classes/', permanent=False)),
]