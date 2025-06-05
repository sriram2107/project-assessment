"""
Serializers for the fitness booking API.
"""
from rest_framework import serializers
from .models import FitnessClass, Booking


class FitnessClassSerializer(serializers.ModelSerializer):
    """Serializer for the FitnessClass model."""
    
    class Meta:
        model = FitnessClass
        fields = [
            'id', 'name', 'class_type', 'datetime', 
            'instructor', 'total_slots', 'available_slots'
        ]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for the Booking model."""
    
    class_details = FitnessClassSerializer(source='fitness_class', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client_name', 'client_email', 'booking_time', 'class_details']
        read_only_fields = ['booking_time']
    
    def validate(self, data):
        """Validate the booking data."""
        fitness_class = data.get('fitness_class')
        
        # Check if the class exists
        if not fitness_class:
            raise serializers.ValidationError({"fitness_class": "Class not found."})
        
        # Check if the class is in the past
        if not fitness_class.is_upcoming():
            raise serializers.ValidationError({"fitness_class": "Cannot book a class that has already started or ended."})
        
        # Check if there are available slots
        if not fitness_class.has_available_slots():
            raise serializers.ValidationError({"fitness_class": "No available slots for this class."})
        
        # Check if the client has already booked this class
        client_email = data.get('client_email')
        if Booking.objects.filter(fitness_class=fitness_class, client_email=client_email).exists():
            raise serializers.ValidationError({"client_email": "You have already booked this class."})
        
        return data
    
    def create(self, validated_data):
        """Create a new booking and update available slots."""
        fitness_class = validated_data.get('fitness_class')
        
        # Book a slot in the fitness class
        if not fitness_class.book_slot():
            raise serializers.ValidationError({"fitness_class": "Failed to book a slot for this class."})
        
        # Create the booking
        booking = Booking.objects.create(**validated_data)
        return booking


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for booking creation requests."""
    
    class_id = serializers.IntegerField()
    client_name = serializers.CharField(max_length=100)
    client_email = serializers.EmailField()
    
    def validate_class_id(self, value):
        """Validate the class_id field."""
        try:
            fitness_class = FitnessClass.objects.get(pk=value)
            
            # Check if the class is in the past
            if not fitness_class.is_upcoming():
                raise serializers.ValidationError("Cannot book a class that has already started or ended.")
            
            # Check if there are available slots
            if not fitness_class.has_available_slots():
                raise serializers.ValidationError("No available slots for this class.")
            
            return value
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Class not found.")