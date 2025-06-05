"""
Models for the fitness booking API.
"""
from django.db import models
from django.utils import timezone
import pytz


class FitnessClass(models.Model):
    """Model representing a fitness class."""
    
    CLASS_TYPES = (
        ('YOGA', 'Yoga'),
        ('ZUMBA', 'Zumba'),
        ('HIIT', 'HIIT'),
        ('PILATES', 'Pilates'),
        ('CYCLING', 'Cycling'),
    )
    
    name = models.CharField(max_length=100)
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES)
    datetime = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    total_slots = models.PositiveIntegerField(default=20)
    available_slots = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.class_type} class by {self.instructor} on {self.datetime}"
    
    def update_timezone(self, timezone_str):
        """Update the class datetime to a different timezone."""
        if not timezone_str in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {timezone_str}")
        
        # Get the current timezone from settings
        current_tz = pytz.timezone(timezone.get_current_timezone_name())
        
        # Convert to the new timezone
        new_tz = pytz.timezone(timezone_str)
        
        # Localize the datetime to the current timezone first, then convert
        current_datetime = current_tz.localize(self.datetime.replace(tzinfo=None))
        new_datetime = current_datetime.astimezone(new_tz)
        
        self.datetime = new_datetime
        self.save()
    
    def is_upcoming(self):
        """Check if the class is in the future."""
        return self.datetime > timezone.now()
    
    def has_available_slots(self):
        """Check if the class has available slots."""
        return self.available_slots > 0
    
    def book_slot(self):
        """Book a slot in the class."""
        if not self.has_available_slots():
            return False
        
        self.available_slots -= 1
        self.save()
        return True


class Booking(models.Model):
    """Model representing a booking for a fitness class."""
    
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    booking_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # One client can't book the same class twice
        unique_together = ('fitness_class', 'client_email')
    
    def __str__(self):
        return f"{self.client_name} booked {self.fitness_class.name}"