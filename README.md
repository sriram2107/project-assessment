# Fitness Studio Booking API

A simple RESTful API for managing fitness class bookings, built with Django and Django REST Framework.

## Features

- View all upcoming fitness classes
- Book a spot in a fitness class
- View all bookings for a specific email address
- Update timezone for all classes

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fitness-booking-api
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Seed the database with sample data:
   ```
   python manage.py seed_data
   ```

5. Run the server:
   ```
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`.

## API Endpoints

### GET /api/classes/

Returns a list of all upcoming fitness classes.

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Morning Yoga",
    "class_type": "YOGA",
    "datetime": "2023-11-14T08:00:00Z",
    "instructor": "John Smith",
    "total_slots": 20,
    "available_slots": 15
  },
  {
    "id": 2,
    "name": "HIIT Workout",
    "class_type": "HIIT",
    "datetime": "2023-11-14T17:30:00Z",
    "instructor": "Jane Doe",
    "total_slots": 15,
    "available_slots": 5
  }
]
```

### POST /api/book/

Books a spot in a fitness class.

**Request Body:**
```json
{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john.doe@example.com"
}
```

**Example Response:**
```json
{
  "id": 1,
  "fitness_class": 1,
  "client_name": "John Doe",
  "client_email": "john.doe@example.com",
  "booking_time": "2023-11-13T14:30:45Z",
  "class_details": {
    "id": 1,
    "name": "Morning Yoga",
    "class_type": "YOGA",
    "datetime": "2023-11-14T08:00:00Z",
    "instructor": "John Smith",
    "total_slots": 20,
    "available_slots": 14
  }
}
```

### GET /api/bookings/?email=john.doe@example.com

Returns all bookings for a specific email address.

**Example Response:**
```json
[
  {
    "id": 1,
    "fitness_class": 1,
    "client_name": "John Doe",
    "client_email": "john.doe@example.com",
    "booking_time": "2023-11-13T14:30:45Z",
    "class_details": {
      "id": 1,
      "name": "Morning Yoga",
      "class_type": "YOGA",
      "datetime": "2023-11-14T08:00:00Z",
      "instructor": "John Smith",
      "total_slots": 20,
      "available_slots": 14
    }
  }
]
```

### POST /api/timezone/

Updates the timezone for all classes.

**Request Body:**
```json
{
  "timezone": "America/New_York"
}
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Morning Yoga",
    "class_type": "YOGA",
    "datetime": "2023-11-13T22:00:00-05:00",
    "instructor": "John Smith",
    "total_slots": 20,
    "available_slots": 14
  },
  {
    "id": 2,
    "name": "HIIT Workout",
    "class_type": "HIIT",
    "datetime": "2023-11-14T07:30:00-05:00",
    "instructor": "Jane Doe",
    "total_slots": 15,
    "available_slots": 5
  }
]
```

## Sample cURL Requests

### Get all classes
```bash
curl -X GET http://127.0.0.1:8000/api/classes/
```

### Book a class
```bash
curl -X POST http://127.0.0.1:8000/api/book/ \
  -H "Content-Type: application/json" \
  -d '{"class_id": 1, "client_name": "John Doe", "client_email": "john.doe@example.com"}'
```

### Get bookings for an email
```bash
curl -X GET "http://127.0.0.1:8000/api/bookings/?email=john.doe@example.com"
```

### Update timezone
```bash
curl -X POST http://127.0.0.1:8000/api/timezone/ \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/New_York"}'
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400 Bad Request: For validation errors (e.g., missing fields, already booked)
- 404 Not Found: When a requested resource doesn't exist
- 500 Internal Server Error: For server-side errors

## Testing

Run the tests with:
```
python manage.py test
```