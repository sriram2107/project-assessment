"""
URL patterns for the booking API.
"""
from django.urls import path
from .views import (
    FitnessClassListView, 
    BookingCreateView, 
    BookingListView,
    TimezoneUpdateView
)

urlpatterns = [
    path('classes/', FitnessClassListView.as_view(), name='classes-list'),
    path('book/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/', BookingListView.as_view(), name='bookings-list'),
    path('timezone/', TimezoneUpdateView.as_view(), name='timezone-update'),
]