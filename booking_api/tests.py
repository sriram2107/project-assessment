"""
Tests for the fitness booking API.
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import datetime
import json

from .models import FitnessClass, Booking


class FitnessClassModelTests(TestCase):
    """Test cases for the FitnessClass model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a fitness class in the future
        self.future_class = FitnessClass.objects.create(
            name="Morning Yoga",
            class_type="YOGA",
            datetime=timezone.now() + datetime.timedelta(days=1),
            instructor="John Doe",
            total_slots=20,
            available_slots=20
        )
        
        # Create a fitness class in the past
        self.past_class = FitnessClass.objects.create(
            name="Evening HIIT",
            class_type="HIIT",
            datetime=timezone.now() - datetime.timedelta(days=1),
            instructor="Jane Smith",
            total_slots=15,
            available_slots=0
        )
    
    def test_is_upcoming(self):
        """Test the is_upcoming method."""
        self.assertTrue(self.future_class.is_upcoming())
        self.assertFalse(self.past_class.is_upcoming())
    
    def test_has_available_slots(self):
        """Test the has_available_slots method."""
        self.assertTrue(self.future_class.has_available_slots())
        self.assertFalse(self.past_class.has_available_slots())
    
    def test_book_slot(self):
        """Test the book_slot method."""
        # Book a slot in the future class
        self.assertTrue(self.future_class.book_slot())
        self.assertEqual(self.future_class.available_slots, 19)
        
        # Try to book a slot in the past class
        self.assertFalse(self.past_class.book_slot())
        self.assertEqual(self.past_class.available_slots, 0)


class APITests(TestCase):
    """Test cases for the API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a fitness class in the future
        self.future_class = FitnessClass.objects.create(
            name="Morning Yoga",
            class_type="YOGA",
            datetime=timezone.now() + datetime.timedelta(days=1),
            instructor="John Doe",
            total_slots=20,
            available_slots=20
        )
        
        # Create a fitness class in the past
        self.past_class = FitnessClass.objects.create(
            name="Evening HIIT",
            class_type="HIIT",
            datetime=timezone.now() - datetime.timedelta(days=1),
            instructor="Jane Smith",
            total_slots=15,
            available_slots=0
        )
        
        # Create a booking
        self.booking = Booking.objects.create(
            fitness_class=self.future_class,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        # Update the available slots
        self.future_class.available_slots = 19
        self.future_class.save()
    
    def test_get_classes(self):
        """Test the GET /classes endpoint."""
        response = self.client.get('/api/classes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Only future classes should be returned
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.future_class.name)
    
    def test_create_booking(self):
        """Test the POST /book endpoint."""
        # Valid booking
        response = self.client.post('/api/book/', {
            'class_id': self.future_class.id,
            'client_name': 'New User',
            'client_email': 'new@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the available slots were updated
        self.future_class.refresh_from_db()
        self.assertEqual(self.future_class.available_slots, 18)
        
        # Try to book the same class again with the same email
        response = self.client.post('/api/book/', {
            'class_id': self.future_class.id,
            'client_name': 'New User',
            'client_email': 'new@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Try to book a class that's in the past
        response = self.client.post('/api/book/', {
            'class_id': self.past_class.id,
            'client_name': 'New User',
            'client_email': 'new@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_bookings(self):
        """Test the GET /bookings endpoint."""
        # Get bookings for an email that has bookings
        response = self.client.get('/api/bookings/', {'email': 'test@example.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['client_email'], 'test@example.com')
        
        # Get bookings for an email that has no bookings
        response = self.client.get('/api/bookings/', {'email': 'nonexistent@example.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 0)
        
        # Try to get bookings without providing an email
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)