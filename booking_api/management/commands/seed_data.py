"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
import random

from booking_api.models import FitnessClass, Booking


class Command(BaseCommand):
    """Command to seed the database with sample data."""
    
    help = 'Seed the database with sample data'
    
    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write('Seeding database...')
        
        # Clear existing data
        FitnessClass.objects.all().delete()
        Booking.objects.all().delete()
        
        # Create fitness classes
        self._create_fitness_classes()
        
        # Create bookings
        self._create_bookings()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
    
    def _create_fitness_classes(self):
        """Create sample fitness classes."""
        # Class types
        class_types = ['YOGA', 'ZUMBA', 'HIIT', 'PILATES', 'CYCLING']
        
        # Class names for each type
        class_names = {
            'YOGA': ['Morning Yoga', 'Power Yoga', 'Relaxation Yoga', 'Yoga for Beginners'],
            'ZUMBA': ['Zumba Dance', 'Zumba Fitness', 'High Energy Zumba'],
            'HIIT': ['HIIT Workout', 'Intense HIIT', 'HIIT for Weight Loss'],
            'PILATES': ['Core Pilates', 'Pilates for Flexibility', 'Power Pilates'],
            'CYCLING': ['Cycling Class', 'Spin Session', 'Endurance Cycling']
        }
        
        # Instructors
        instructors = [
            'John Smith', 'Jane Doe', 'Alice Johnson', 'Bob Williams',
            'Eva Brown', 'Michael Davis', 'Sophia Wilson', 'Ethan Taylor'
        ]
        
        # Get current time
        now = timezone.now()
        
        # Create classes for the next 14 days
        for day in range(1, 15):
            # Create 3-5 classes per day
            for _ in range(random.randint(3, 5)):
                # Random class type
                class_type = random.choice(class_types)
                
                # Random class name based on type
                name = random.choice(class_names[class_type])
                
                # Random instructor
                instructor = random.choice(instructors)
                
                # Random time between 6:00 and 20:00
                hour = random.randint(6, 20)
                minute = random.choice([0, 15, 30, 45])
                
                # Create datetime
                class_datetime = now + datetime.timedelta(days=day)
                class_datetime = class_datetime.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                
                # Random total slots between 10 and 30
                total_slots = random.randint(10, 30)
                
                # Create the class
                FitnessClass.objects.create(
                    name=name,
                    class_type=class_type,
                    datetime=class_datetime,
                    instructor=instructor,
                    total_slots=total_slots,
                    available_slots=total_slots
                )
        
        self.stdout.write(f'Created {FitnessClass.objects.count()} fitness classes')
    
    def _create_bookings(self):
        """Create sample bookings."""
        # Client names
        first_names = [
            'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer',
            'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis',
            'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas'
        ]
        
        # Email domains
        email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        
        # Get all classes
        classes = FitnessClass.objects.all()
        
        # Create bookings
        bookings_count = 0
        
        for fitness_class in classes:
            # Create 0-15 bookings per class
            for _ in range(random.randint(0, min(15, fitness_class.total_slots))):
                # Random client name
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                client_name = f"{first_name} {last_name}"
                
                # Random client email
                email_username = f"{first_name.lower()}.{last_name.lower()}"
                email_domain = random.choice(email_domains)
                client_email = f"{email_username}@{email_domain}"
                
                # Create the booking if there are available slots
                if fitness_class.has_available_slots():
                    # Check if this email has already booked this class
                    if not Booking.objects.filter(
                        fitness_class=fitness_class, 
                        client_email=client_email
                    ).exists():
                        Booking.objects.create(
                            fitness_class=fitness_class,
                            client_name=client_name,
                            client_email=client_email
                        )
                        
                        # Update available slots
                        fitness_class.available_slots -= 1
                        fitness_class.save()
                        
                        bookings_count += 1
        
        self.stdout.write(f'Created {bookings_count} bookings')