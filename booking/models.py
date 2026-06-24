"""
TravelEase - Booking App Models
models.py - Database schema for the entire booking system

This file defines ALL database tables (models) for TravelEase:

TABLES:
1. Bus        - Stores bus schedules (200+ dummy records)
2. BusImage   - Stores bus photos
3. Flight     - Stores flight schedules (200+ dummy records combined)
4. FlightImage- Stores flight photos (optional)
5. Booking    - Stores ticket bookings (links user → bus/flight + seat + payment)
6. Payment    - Stores payment records (dummy Khalti/eSewa)

Each model is a Python class that Django converts to a database table.
Django's ORM (Object-Relational Mapper) handles all SQL automatically.

WHY POSTGRESQL?
- Stores binary image data efficiently (bus/flight photos)
- Handles concurrent bookings with row-level locking
- Faster for complex queries (searching 200+ schedules)
- Better for production scaling than SQLite
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, date


# =============================================
# BUS MODEL
# =============================================
# Stores all bus schedule records
# Each row = one bus trip (route + date + time + price + seats)
class Bus(models.Model):
    """
    Bus Model:
    - Represents a single bus trip/schedule
    - Contains route info, timing, pricing, and seat count
    - Admin can add/edit/delete bus schedules from admin panel
    - Images are stored in a separate BusImage model (one bus → many images)
    """

    # BUS_NUMBER: Unique identifier like "BA 1 KHA 1234" or "NB-001"
    bus_number = models.CharField(
        max_length=20, unique=True,
        help_text="Unique bus registration/route number"
    )

    # BUS_NAME: Operator name like "Mountain Travels", "Greenline", "SkyBus"
    bus_name = models.CharField(
        max_length=100,
        help_text="Bus operator/company name"
    )

    # BUS_TYPE: Type of bus service
    BUS_TYPE_CHOICES = [
        ('AC', 'A/C Deluxe'),
        ('NON_AC', 'Non A/C'),
        ('SLEEPER', 'Sleeper'),
        ('SEMI_SLEEPER', 'Semi Sleeper'),
        ('VOLVO', 'Volvo'),
        ('TATA', 'Tata'),
        ('MINI', 'Mini Bus'),
    ]
    bus_type = models.CharField(
        max_length=20, choices=BUS_TYPE_CHOICES, default='AC',
        help_text="Type/category of bus"
    )

    # DEPARTURE / DESTINATION: Route cities
    departure_city = models.CharField(max_length=100, db_index=True)
    destination_city = models.CharField(max_length=100, db_index=True)

    # DEPARTURE DATE: When the bus departs
    departure_date = models.DateField(db_index=True)

    # DEPARTURE TIME: Scheduled departure time (e.g., "07:00 AM")
    departure_time = models.TimeField()

    # ARRIVAL TIME: Estimated arrival time
    arrival_time = models.TimeField()

    # DURATION: Trip duration as string (e.g., "8 hours", "10h 30m")
    duration = models.CharField(max_length=30, default="8 hours")

    # PRICE: Ticket price per seat (in NPR - Nepalese Rupees)
    # Using DecimalField for accurate currency (not FloatField which has rounding issues)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Price per seat in NPR"
    )

    # TOTAL_SEATS: Total number of seats on the bus
    total_seats = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(10), MaxValueValidator(60)],
        help_text="Total seat capacity"
    )

    # AVAILABLE_SEATS: Dynamically updated as bookings happen
    # Starts equal to total_seats, decreases with each booking
    available_seats = models.PositiveIntegerField(default=40)

    # AMENITIES: Comma-separated list of facilities
    # e.g., "WiFi, Charging Port, Blanket, Water Bottle"
    amenities = models.TextField(
        blank=True,
        help_text="Amenities separated by commas"
    )

    # PICKUP_POINT: Where passengers board
    pickup_point = models.CharField(max_length=200, blank=True)

    # DROPOFF_POINT: Where passengers alight
    dropoff_point = models.CharField(max_length=200, blank=True)

    # IS_ACTIVE: Soft-delete flag (inactive buses won't show in search)
    is_active = models.BooleanField(default=True)

    # CREATED_AT / UPDATED_AT: Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Meta class defines model-level options
        # Order buses by departure date (newest first)
        ordering = ['departure_date', 'departure_time']
        # Index for faster search queries
        indexes = [
            models.Index(fields=['departure_city', 'destination_city', 'departure_date']),
        ]
        # Human-readable name in admin panel
        verbose_name_plural = 'Buses'

    def __str__(self):
        """String representation: 'SkyBus: Kathmandu → Pokhara (2024-01-15)'"""
        return f"{self.bus_name}: {self.departure_city} → {self.destination_city} ({self.departure_date})"

    def is_fully_booked(self):
        """Check if no seats remain"""
        return self.available_seats <= 0

    def get_booked_seats(self):
        """Get list of all booked seat numbers for this bus"""
        bookings = self.booking_set.filter(status__in=['CONFIRMED', 'PENDING'])
        booked = []
        for b in bookings:
            if b.seat_number:
                booked.append(b.seat_number)
        return booked

    def get_amenities_list(self):
        """Convert comma-separated amenities string to list"""
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []


# =============================================
# BUS IMAGE MODEL
# =============================================
# Stores bus photos (multiple images per bus)
# Images are uploaded to media/buses/ directory
class BusImage(models.Model):
    """
    BusImage Model:
    - Allows multiple photos per bus
    - Images stored in media/buses/ folder
    - Uses ImageField which handles upload, storage, and serving
    """
    bus = models.ForeignKey(
        Bus, on_delete=models.CASCADE,
        related_name='images',
        help_text="The bus this image belongs to"
    )
    image = models.ImageField(
        upload_to='buses/',
        help_text="Bus photo (uploaded to media/buses/)"
    )
    caption = models.CharField(
        max_length=200, blank=True,
        help_text="Optional image caption"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Set as main/display image for the bus"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Image for {self.bus.bus_name} ({self.id})"


# =============================================
# FLIGHT MODEL
# =============================================
# Stores all flight schedule records
# Each row = one flight trip (route + date + time + price)
class Flight(models.Model):
    """
    Flight Model:
    - Represents a single flight trip/schedule
    - Structure mirrors Bus model for consistency
    - Separate model allows different fields and validations
    """

    # FLIGHT_NUMBER: Unique identifier like "RA-101" or "YT-502"
    flight_number = models.CharField(
        max_length=20, unique=True,
        help_text="Unique flight number (e.g., RA-101)"
    )

    # AIRLINE: Airline company name
    airline = models.CharField(
        max_length=100,
        help_text="Airline name (e.g., Buddha Air, Yeti Airlines)"
    )

    # FLIGHT_TYPE: Domestic or International
    FLIGHT_TYPE_CHOICES = [
        ('DOMESTIC', 'Domestic'),
        ('INTERNATIONAL', 'International'),
    ]
    flight_type = models.CharField(
        max_length=15, choices=FLIGHT_TYPE_CHOICES, default='DOMESTIC'
    )

    # DEPARTURE / DESTINATION: Route airports/cities
    departure_city = models.CharField(max_length=100, db_index=True)
    destination_city = models.CharField(max_length=100, db_index=True)

    # DEPARTURE DATE & TIME
    departure_date = models.DateField(db_index=True)
    departure_time = models.TimeField()

    # ARRIVAL TIME & DURATION
    arrival_time = models.TimeField()
    duration = models.CharField(max_length=30, default="1 hour")

    # PRICE: Per seat in NPR
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Price per seat in NPR"
    )

    # TOTAL_SEATS & AVAILABLE_SEATS
    total_seats = models.PositiveIntegerField(
        default=120,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Total seat capacity"
    )
    available_seats = models.PositiveIntegerField(default=120)

    # TERMINAL / GATE info
    terminal = models.CharField(max_length=50, blank=True, help_text="Airport terminal")
    gate = models.CharField(max_length=20, blank=True, help_text="Boarding gate")

    # IS_ACTIVE: Soft-delete flag
    is_active = models.BooleanField(default=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['departure_date', 'departure_time']
        indexes = [
            models.Index(fields=['departure_city', 'destination_city', 'departure_date']),
        ]
        verbose_name_plural = 'Flights'

    def __str__(self):
        return f"{self.airline} {self.flight_number}: {self.departure_city} → {self.destination_city} ({self.departure_date})"

    def is_fully_booked(self):
        return self.available_seats <= 0

    def get_booked_seats(self):
        bookings = self.booking_set.filter(status__in=['CONFIRMED', 'PENDING'])
        return [b.seat_number for b in bookings if b.seat_number]


# =============================================
# FLIGHT IMAGE MODEL (Optional)
# =============================================
class FlightImage(models.Model):
    """Stores airline/flight images"""
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='flights/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Image for {self.flight.airline} ({self.id})"


# =============================================
# BOOKING MODEL
# =============================================
# The core model that ties everything together:
# User books → a Bus OR Flight → selects a Seat → makes a Payment
class Booking(models.Model):
    """
    Booking Model - The central transaction record.

    Each booking:
    - Is made by one User
    - Is for EITHER a Bus OR a Flight (not both)
    - Has exactly one Seat Number
    - Has passenger details
    - Has a booking status (PENDING → CONFIRMED after payment)
    - Generates a unique booking reference number
    - Links to a Payment record
    """

    # BOOKING_REFERENCE: Unique ID like "TRE-20240115-ABC123"
    # Generated automatically when booking is created
    booking_reference = models.CharField(
        max_length=50, unique=True,
        help_text="Unique booking reference number"
    )

    # USER: Who made the booking
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        help_text="User who made this booking"
    )

    # BOOKING_TYPE: Bus or Flight
    BOOKING_TYPE_CHOICES = [
        ('BUS', 'Bus'),
        ('FLIGHT', 'Flight'),
    ]
    booking_type = models.CharField(
        max_length=10, choices=BOOKING_TYPE_CHOICES,
        help_text="Type of transport booked"
    )

    # BUS: Link to Bus model (nullable - only set if booking_type='BUS')
    bus = models.ForeignKey(
        Bus, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='booking_set',
        help_text="Bus if this is a bus booking"
    )

    # FLIGHT: Link to Flight model (nullable - only set if booking_type='FLIGHT')
    flight = models.ForeignKey(
        Flight, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='booking_set',
        help_text="Flight if this is a flight booking"
    )

    # PASSENGER DETAILS
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=15)
    passenger_age = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    passenger_gender = models.CharField(
        max_length=10,
        choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
        blank=True
    )

    # SEAT_NUMBER: Selected seat (e.g., "A1", "B12", "3A")
    seat_number = models.CharField(max_length=10)

    # NUMBER OF SEATS BOOKED (for future multi-seat booking)
    number_of_seats = models.PositiveIntegerField(default=1)

    # TOTAL PRICE for this booking
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # BOOKING STATUS
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='PENDING',
        help_text="Current status of the booking"
    )

    # TIMESTAMPS
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.passenger_name} ({self.status})"

    def save(self, *args, **kwargs):
        """Override save to auto-generate booking reference on first creation"""
        if not self.booking_reference:
            import uuid
            # Generate unique reference: TRE-YYYYMMDD-RANDOM
            date_str = date.today().strftime('%Y%m%d')
            random_str = uuid.uuid4().hex[:8].upper()
            self.booking_reference = f"TRE-{date_str}-{random_str}"
        super().save(*args, **kwargs)

    def get_transport_name(self):
        """Get the transport name for display"""
        if self.booking_type == 'BUS' and self.bus:
            return f"{self.bus.bus_name} ({self.bus.bus_number})"
        elif self.booking_type == 'FLIGHT' and self.flight:
            return f"{self.flight.airline} ({self.flight.flight_number})"
        return "N/A"

    def get_route(self):
        """Get the route string"""
        if self.booking_type == 'BUS' and self.bus:
            return f"{self.bus.departure_city} → {self.bus.destination_city}"
        elif self.booking_type == 'FLIGHT' and self.flight:
            return f"{self.flight.departure_city} → {self.flight.destination_city}"
        return "N/A"

    def get_departure_datetime(self):
        """Get the departure date and time"""
        if self.booking_type == 'BUS' and self.bus:
            return f"{self.bus.departure_date} at {self.bus.departure_time}"
        elif self.booking_type == 'FLIGHT' and self.flight:
            return f"{self.flight.departure_date} at {self.flight.departure_time}"
        return "N/A"


# =============================================
# PAYMENT MODEL
# =============================================
# Stores payment records for each booking
# Simulates Khalti/eSewa payment workflow
class Payment(models.Model):
    """
    Payment Model:
    - Each booking has exactly ONE payment record
    - Stores payment method (Khalti/eSewa dummy), amount, status
    - Transaction ID is simulated (not real)
    """

    # BOOKING: One-to-one link to Booking
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE,
        help_text="Booking this payment is for"
    )

    # PAYMENT METHOD
    PAYMENT_METHOD_CHOICES = [
        ('KHALTI', 'Khalti'),
        ('ESEWA', 'eSewa'),
    ]
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES,
        help_text="Dummy payment gateway used"
    )

    # AMOUNT: Should match booking.total_price
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # TRANSACTION ID: Simulated unique ID
    transaction_id = models.CharField(
        max_length=100, unique=True,
        help_text="Simulated transaction reference"
    )

    # PAYMENT STATUS
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING'
    )

    # TIMESTAMPS
    payment_date = models.DateTimeField(auto_now_add=True)

    # REMARKS: Any additional notes
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.payment_method} ({self.payment_status})"

    def save(self, *args, **kwargs):
        """Auto-generate transaction ID"""
        if not self.transaction_id:
            import uuid
            prefix = 'KLT' if self.payment_method == 'KHALTI' else 'ESW'
            self.transaction_id = f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
