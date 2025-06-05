"""
Views for the fitness booking API.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import FitnessClass, Booking
from .serializers import (
    FitnessClassSerializer, 
    BookingSerializer,
    BookingCreateSerializer
)

# Set up logging
logger = logging.getLogger(__name__)


class FitnessClassListView(APIView):
    """
    API view to retrieve a list of all upcoming fitness classes.
    """
    
    def get(self, request):
        """
        GET method to retrieve all upcoming fitness classes.
        """
        # Get the current time
        now = timezone.now()
        
        # Filter classes that are in the future
        classes = FitnessClass.objects.filter(datetime__gt=now).order_by('datetime')
        
        # Serialize the data
        serializer = FitnessClassSerializer(classes, many=True)
        
        logger.info(f"Retrieved {len(classes)} upcoming fitness classes")
        return Response(serializer.data)


class BookingCreateView(APIView):
    """
    API view to create a new booking.
    """
    
    def post(self, request):
        """
        POST method to create a new booking.
        """
        # First validate the request data
        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid booking request: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the validated data
        validated_data = serializer.validated_data
        class_id = validated_data.get('class_id')
        client_name = validated_data.get('client_name')
        client_email = validated_data.get('client_email')
        
        # Get the fitness class
        try:
            fitness_class = FitnessClass.objects.get(pk=class_id)
        except FitnessClass.DoesNotExist:
            logger.warning(f"Fitness class not found: {class_id}")
            return Response(
                {"error": "Fitness class not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the client has already booked this class
        if Booking.objects.filter(fitness_class=fitness_class, client_email=client_email).exists():
            logger.warning(f"Client {client_email} has already booked class {class_id}")
            return Response(
                {"error": "You have already booked this class"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to book a slot
        if not fitness_class.book_slot():
            logger.warning(f"No available slots for class {class_id}")
            return Response(
                {"error": "No available slots for this class"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the booking
        booking = Booking.objects.create(
            fitness_class=fitness_class,
            client_name=client_name,
            client_email=client_email
        )
        
        # Serialize the booking
        booking_serializer = BookingSerializer(booking)
        
        logger.info(f"Created booking {booking.id} for client {client_email}")
        return Response(booking_serializer.data, status=status.HTTP_201_CREATED)


class BookingListView(APIView):
    """
    API view to retrieve all bookings for a specific email address.
    """
    
    def get(self, request):
        """
        GET method to retrieve all bookings for a specific email address.
        """
        # Get the email from the query parameters
        email = request.query_params.get('email')
        
        # Check if the email is provided
        if not email:
            logger.warning("Email parameter is required")
            return Response(
                {"error": "Email parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all bookings for the email
        bookings = Booking.objects.filter(client_email=email).order_by('-booking_time')
        
        # Serialize the bookings
        serializer = BookingSerializer(bookings, many=True)
        
        logger.info(f"Retrieved {len(bookings)} bookings for email {email}")
        return Response(serializer.data)


class TimezoneUpdateView(APIView):
    """
    API view to update the timezone of all classes.
    """
    
    def post(self, request):
        """
        POST method to update the timezone of all classes.
        """
        # Get the timezone from the request data
        timezone_str = request.data.get('timezone')
        
        # Check if the timezone is provided
        if not timezone_str:
            logger.warning("Timezone parameter is required")
            return Response(
                {"error": "Timezone parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the timezone is valid
        try:
            import pytz
            if not timezone_str in pytz.all_timezones:
                logger.warning(f"Invalid timezone: {timezone_str}")
                return Response(
                    {"error": f"Invalid timezone: {timezone_str}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ImportError:
            logger.warning("pytz module not found")
            return Response(
                {"error": "Server configuration error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update the timezone for all classes
        classes = FitnessClass.objects.all()
        for fitness_class in classes:
            try:
                fitness_class.update_timezone(timezone_str)
            except Exception as e:
                logger.error(f"Error updating timezone for class {fitness_class.id}: {e}")
                return Response(
                    {"error": f"Error updating timezone: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Return the updated classes
        updated_classes = FitnessClass.objects.filter(datetime__gt=timezone.now()).order_by('datetime')
        serializer = FitnessClassSerializer(updated_classes, many=True)
        
        logger.info(f"Updated timezone to {timezone_str} for {len(classes)} classes")
        return Response(serializer.data)