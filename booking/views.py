"""
TravelEase - Booking App Views
views.py - Core booking functionality

Handles:
- Homepage
- Bus search (by departure, destination, date)
- Flight search (by departure, destination, date)
- Bus/Flight detail page (schedule info, seat map)
- Seat selection and booking
- Booking confirmation page
- Booking cancellation
- Booking detail (individual booking view)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from datetime import date, datetime
from .models import Bus, Flight, Booking, Payment, BusImage, FlightImage


# =============================================
# HOMEPAGE VIEW
# =============================================
def home(request):
    """
    TravelEase Homepage.

    Displays:
    - Search form (tabs for Bus / Flight)
    - Quick stats (total routes, happy customers, etc.)
    - Featured/popular routes
    - Latest bus schedules (upcoming)
    - Latest flight schedules (upcoming)

    This is the landing page for ALL users (guests + logged in).
    """
    # Get upcoming buses (departure date >= today)
    upcoming_buses = Bus.objects.filter(
        departure_date__gte=date.today(),
        is_active=True
    ).order_by('departure_date', 'departure_time')[:6]

    # Get upcoming flights
    upcoming_flights = Flight.objects.filter(
        departure_date__gte=date.today(),
        is_active=True
    ).order_by('departure_date', 'departure_time')[:6]

    # Distinct cities actually present in the database
    bus_departure_cities = sorted(
        Bus.objects.filter(is_active=True)
        .values_list('departure_city', flat=True)
        .distinct()
    )
    bus_destination_cities = sorted(
        Bus.objects.filter(is_active=True)
        .values_list('destination_city', flat=True)
        .distinct()
    )
    flight_departure_cities = sorted(
        Flight.objects.filter(is_active=True)
        .values_list('departure_city', flat=True)
        .distinct()
    )
    flight_destination_cities = sorted(
        Flight.objects.filter(is_active=True)
        .values_list('destination_city', flat=True)
        .distinct()
    )

    # Stats for homepage
    total_buses = Bus.objects.filter(is_active=True).count()
    total_flights = Flight.objects.filter(is_active=True).count()
    total_routes = Bus.objects.filter(is_active=True).values(
        'departure_city', 'destination_city'
    ).distinct().count()

    context = {
        'upcoming_buses': upcoming_buses,
        'upcoming_flights': upcoming_flights,
        'bus_departure_cities': bus_departure_cities,
        'bus_destination_cities': bus_destination_cities,
        'flight_departure_cities': flight_departure_cities,
        'flight_destination_cities': flight_destination_cities,
        'total_buses': total_buses,
        'total_flights': total_flights,
        'total_routes': total_routes,
        'today': date.today(),
    }
    return render(request, 'booking/home.html', context)


# =============================================
# BUS SEARCH VIEW
# =============================================
def search_buses(request):
    """
    Search Buses by route and date.

    QUERY PARAMETERS (GET):
    - departure: city name (e.g., 'Kathmandu')
    - destination: city name (e.g., 'Pokhara')
    - date: departure date (YYYY-MM-DD)

    FILTERING LOGIC:
    - Case-insensitive partial matching using __icontains
    - Date filtering using __gte (greater than or equal)
    - Only active buses (is_active=True)
    - Only buses with available seats
    """
    buses = Bus.objects.filter(is_active=True, departure_date__gte=date.today())

    departure = request.GET.get('departure', '').strip()
    destination = request.GET.get('destination', '').strip()
    travel_date = request.GET.get('date', '').strip()

    if departure:
        # __icontains = case-insensitive "contains" (LIKE '%value%' in SQL)
        buses = buses.filter(departure_city__icontains=departure)

    if destination:
        buses = buses.filter(destination_city__icontains=destination)

    if travel_date:
        try:
            travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
            buses = buses.filter(departure_date=travel_date_obj)
        except ValueError:
            messages.warning(request, 'Invalid date format. Showing all dates.')

    # Order results
    buses = buses.order_by('departure_date', 'departure_time')

    # Get unique cities for autocomplete suggestions
    all_cities = Bus.objects.filter(is_active=True).values_list(
        'departure_city', flat=True
    ).distinct().order_by('departure_city')

    context = {
        'buses': buses,
        'departure': departure,
        'destination': destination,
        'travel_date': travel_date,
        'all_cities': all_cities,
        'result_count': buses.count(),
        'search_type': 'Bus',
    }
    return render(request, 'booking/search_results.html', context)


# =============================================
# FLIGHT SEARCH VIEW
# =============================================
def search_flights(request):
    """
    Search Flights by route and date.

    Same logic as search_buses but for Flight model.
    """
    flights = Flight.objects.filter(is_active=True, departure_date__gte=date.today())

    departure = request.GET.get('departure', '').strip()
    destination = request.GET.get('destination', '').strip()
    travel_date = request.GET.get('date', '').strip()

    if departure:
        flights = flights.filter(departure_city__icontains=departure)

    if destination:
        flights = flights.filter(destination_city__icontains=destination)

    if travel_date:
        try:
            travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
            flights = flights.filter(departure_date=travel_date_obj)
        except ValueError:
            messages.warning(request, 'Invalid date format. Showing all dates.')

    flights = flights.order_by('departure_date', 'departure_time')

    all_cities = Flight.objects.filter(is_active=True).values_list(
        'departure_city', flat=True
    ).distinct().order_by('departure_city')

    context = {
        'flights': flights,
        'departure': departure,
        'destination': destination,
        'travel_date': travel_date,
        'all_cities': all_cities,
        'result_count': flights.count(),
        'search_type': 'Flight',
    }
    return render(request, 'booking/search_results.html', context)


# =============================================
# BUS DETAIL VIEW
# =============================================
def bus_detail(request, bus_id):
    """
    Detailed view of a single bus schedule.

    Shows:
    - Bus info (name, type, route, timing, price)
    - Bus images (from BusImage model)
    - Amenities list
    - Seat map (visual grid of available/booked seats)
    - Booking form (if user is logged in)

    The seat map is generated as a grid (e.g., 4 columns × 10 rows for 40 seats)
    Each seat shows: available (green) or booked (red)
    """
    bus = get_object_or_404(Bus, id=bus_id, is_active=True)

    # Get bus images
    bus_images = bus.images.all()

    # Get booked seats for seat map
    booked_seats = bus.get_booked_seats()

    # Generate seat layout
    # For a bus with 40 seats: 4 columns (A,B,C,D) × 10 rows
    total_seats = bus.total_seats
    cols = 4  # A, B, C, D (window, middle, aisle, window)
    rows = (total_seats + cols - 1) // cols  # Ceiling division

    seat_labels = ['A', 'B', 'C', 'D']
    seat_grid = []
    seat_num = 1
    for row in range(rows):
        row_seats = []
        for col in range(cols):
            if seat_num <= total_seats:
                seat_id = f"{seat_labels[col]}{row + 1}"
                is_booked = seat_id in booked_seats
                row_seats.append({
                    'id': seat_id,
                    'number': seat_num,
                    'booked': is_booked,
                    'label': seat_labels[col],
                })
                seat_num += 1
        seat_grid.append(row_seats)

    context = {
        'bus': bus,
        'bus_images': bus_images,
        'booked_seats': booked_seats,
        'seat_grid': seat_grid,
        'available_count': bus.available_seats,
        'amenities': bus.get_amenities_list(),
    }
    return render(request, 'booking/bus_detail.html', context)


# =============================================
# FLIGHT DETAIL VIEW
# =============================================
def flight_detail(request, flight_id):
    """
    Detailed view of a single flight schedule.
    Same structure as bus_detail but for flights.
    """
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    flight_images = flight.images.all()
    booked_seats = flight.get_booked_seats()

    # Generate seat layout for flight
    # Flights typically have 6 seats per row (A,B,C,D,E,F)
    total_seats = flight.total_seats
    cols = 6
    rows = (total_seats + cols - 1) // cols

    seat_labels = ['A', 'B', 'C', 'D', 'E', 'F']
    seat_grid = []
    seat_num = 1
    for row in range(rows):
        row_seats = []
        for col in range(cols):
            if seat_num <= total_seats:
                seat_id = f"{seat_labels[col]}{row + 1}"
                is_booked = seat_id in booked_seats
                row_seats.append({
                    'id': seat_id,
                    'number': seat_num,
                    'booked': is_booked,
                    'label': seat_labels[col],
                })
                seat_num += 1
        seat_grid.append(row_seats)

    context = {
        'flight': flight,
        'flight_images': flight_images,
        'booked_seats': booked_seats,
        'seat_grid': seat_grid,
        'available_count': flight.available_seats,
    }
    return render(request, 'booking/flight_detail.html', context)


# =============================================
# BOOK TICKET VIEW
# =============================================
@login_required
def book_ticket(request):
    """
    Create a new booking (ticket reservation).

    FLOW:
    1. User is on bus/flight detail page
    2. User selects a seat
    3. User fills passenger info (name, email, phone, etc.)
    4. POST data is sent here
    5. Booking is created with status=PENDING
    6. Available seats are decreased
    7. User is redirected to payment page

    VALIDATIONS:
    - User must be logged in
    - Transport (bus/flight) must exist and be active
    - Seat must not already be booked
    - Seat number must be valid
    """
    if request.method != 'POST':
        return redirect('booking:home')

    booking_type = request.POST.get('booking_type', '').strip()
    transport_id = request.POST.get('transport_id', '').strip()
    seat_number = request.POST.get('seat_number', '').strip()
    passenger_name = request.POST.get('passenger_name', '').strip()
    passenger_email = request.POST.get('passenger_email', '').strip()
    passenger_phone = request.POST.get('passenger_phone', '').strip()
    passenger_age = request.POST.get('passenger_age', '').strip()
    passenger_gender = request.POST.get('passenger_gender', '').strip()

    # --- VALIDATION ---
    if not all([booking_type, transport_id, seat_number, passenger_name,
                passenger_email, passenger_phone]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect(request.META.get('HTTP_REFERER', 'booking:home'))

    # Determine if bus or flight
    bus = None
    flight = None
    total_price = 0

    if booking_type == 'BUS':
        bus = get_object_or_404(Bus, id=transport_id, is_active=True)

        # Check if seat is already booked
        if seat_number in bus.get_booked_seats():
            messages.error(request, f'Seat {seat_number} is already booked. Please select another seat.')
            return redirect('booking:bus_detail', bus_id=bus.id)

        # Check if bus has available seats
        if bus.available_seats <= 0:
            messages.error(request, 'Sorry, this bus is fully booked.')
            return redirect('booking:bus_detail', bus_id=bus.id)

        total_price = bus.price
        number_of_seats = 1

    elif booking_type == 'FLIGHT':
        flight = get_object_or_404(Flight, id=transport_id, is_active=True)

        if seat_number in flight.get_booked_seats():
            messages.error(request, f'Seat {seat_number} is already booked.')
            return redirect('booking:flight_detail', flight_id=flight.id)

        if flight.available_seats <= 0:
            messages.error(request, 'Sorry, this flight is fully booked.')
            return redirect('booking:flight_detail', flight_id=flight.id)

        total_price = flight.price
        number_of_seats = 1

    else:
        messages.error(request, 'Invalid booking type.')
        return redirect('booking:home')

    # --- CREATE BOOKING ---
    booking = Booking.objects.create(
        user=request.user,
        booking_type=booking_type,
        bus=bus,
        flight=flight,
        passenger_name=passenger_name,
        passenger_email=passenger_email,
        passenger_phone=passenger_phone,
        passenger_age=int(passenger_age) if passenger_age else None,
        passenger_gender=passenger_gender if passenger_gender else '',
        seat_number=seat_number,
        number_of_seats=number_of_seats,
        total_price=total_price,
        status='PENDING',  # PENDING until payment is made
    )

    # Decrease available seats
    if bus:
        bus.available_seats -= 1
        bus.save()
    if flight:
        flight.available_seats -= 1
        flight.save()

    messages.success(request, f'Seat {seat_number} reserved! Please complete payment to confirm.')
    return redirect('payment:make_payment', booking_id=booking.id)


# =============================================
# BOOKING CONFIRMATION VIEW
# =============================================
@login_required
def booking_confirmation(request, booking_id):
    """
    Show booking confirmation after successful payment.

    Displays:
    - Booking reference number
    - Passenger details
    - Transport details (bus/flight info)
    - Seat number
    - Payment status
    - Download/print option
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Get payment info
    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        payment = None

    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'booking/booking_confirmation.html', context)


# =============================================
# BOOKING DETAIL VIEW
# =============================================
@login_required
def booking_detail(request, booking_id):
    """
    View a specific booking's details.
    Accessible from booking history.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        payment = None

    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'booking/booking_detail.html', context)


# =============================================
# CANCEL BOOKING VIEW
# =============================================
@login_required
def cancel_booking(request, booking_id):
    """
    Cancel a booking.

    Only allowed for PENDING or CONFIRMED bookings.
    Restores the seat to available pool.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking:booking_detail', booking_id=booking.id)

    if request.method == 'POST':
        # Restore seat availability
        if booking.bus:
            booking.bus.available_seats += 1
            booking.bus.save()
        if booking.flight:
            booking.flight.available_seats += 1
            booking.flight.save()

        booking.status = 'CANCELLED'
        booking.save()

        messages.success(request, f'Booking {booking.booking_reference} has been cancelled.')
        return redirect('accounts:profile')

    return render(request, 'booking/cancel_booking.html', {'booking': booking})


# =============================================
# ALL BUSES LIST VIEW
# =============================================
def all_buses(request):
    """List all active bus schedules."""
    buses = Bus.objects.filter(
        is_active=True, departure_date__gte=date.today()
    ).order_by('departure_date', 'departure_time')
    return render(request, 'booking/all_buses.html', {'buses': buses})


# =============================================
# ALL FLIGHTS LIST VIEW
# =============================================
def all_flights(request):
    """List all active flight schedules."""
    flights = Flight.objects.filter(
        is_active=True, departure_date__gte=date.today()
    ).order_by('departure_date', 'departure_time')
    return render(request, 'booking/all_flights.html', {'flights': flights})


# =============================================
# API: GET AVAILABLE SEATS (AJAX)
# =============================================
def get_available_seats(request, transport_type, transport_id):
    """
    AJAX endpoint: Returns JSON of booked seats.
    Used by the seat map to dynamically highlight booked seats.

    Example response: {"booked": ["A1", "A2", "B5"], "total": 40, "available": 37}
    """
    if transport_type == 'bus':
        transport = get_object_or_404(Bus, id=transport_id, is_active=True)
    elif transport_type == 'flight':
        transport = get_object_or_404(Flight, id=transport_id, is_active=True)
    else:
        return JsonResponse({'error': 'Invalid transport type'}, status=400)

    data = {
        'booked': transport.get_booked_seats(),
        'total': transport.total_seats,
        'available': transport.available_seats,
    }
    return JsonResponse(data)
