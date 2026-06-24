"""
TravelEase - Payment App Views
views.py - Dummy Khalti/eSewa payment simulation

Handles:
- Payment page (choose Khalti or eSewa)
- Dummy payment processing
- Payment success/failure
- Email notification after payment
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from booking.models import Booking, Payment


# =============================================
# MAKE PAYMENT VIEW
# =============================================
@login_required
def make_payment(request, booking_id):
    """
    Payment Page — displays booking summary and payment options.

    Shows:
    - Booking summary (transport, route, seat, price)
    - Dummy Khalti button
    - Dummy eSewa button

    User selects a payment method and clicks "Pay Now".
    This simulates a real digital wallet payment flow.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Prevent paying for already paid/cancelled bookings
    if booking.status != 'PENDING':
        messages.warning(request, 'This booking has already been processed.')
        if booking.status == 'CONFIRMED':
            return redirect('booking:booking_confirmation', booking_id=booking.id)
        return redirect('accounts:profile')

    # Check if payment already exists
    try:
        existing_payment = booking.payment
        if existing_payment.payment_status == 'SUCCESS':
            messages.info(request, 'Payment already completed for this booking.')
            return redirect('booking:booking_confirmation', booking_id=booking.id)
    except Payment.DoesNotExist:
        pass

    context = {
        'booking': booking,
    }
    return render(request, 'payment/make_payment.html', context)


# =============================================
# PROCESS PAYMENT VIEW (Dummy)
# =============================================
@login_required
def process_payment(request, booking_id):
    """
    Simulate payment processing.

    This is a DUMMY implementation that:
    1. Creates a Payment record
    2. Simulates payment success (no real money involved)
    3. Updates booking status to CONFIRMED
    4. Sends confirmation email to passenger

    In a REAL application, this would:
    - Call Khalti/eSewa API
    - Verify transaction with the gateway
    - Handle callbacks/webhooks
    """
    if request.method != 'POST':
        return redirect('payment:make_payment', booking_id=booking_id)

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'PENDING':
        messages.warning(request, 'This booking cannot be paid.')
        return redirect('accounts:profile')

    payment_method = request.POST.get('payment_method', 'KHALTI').strip()

    if payment_method not in ['KHALTI', 'ESEWA']:
        messages.error(request, 'Invalid payment method.')
        return redirect('payment:make_payment', booking_id=booking_id)

    # --- CREATE PAYMENT RECORD ---
    # In a real app, this would be created AFTER gateway confirmation
    payment = Payment.objects.create(
        booking=booking,
        payment_method=payment_method,
        amount=booking.total_price,
        payment_status='SUCCESS',  # Simulated success
        remarks=f'Dummy {payment_method} payment - simulated transaction',
    )

    # --- UPDATE BOOKING STATUS ---
    booking.status = 'CONFIRMED'
    booking.save()

    # --- SEND CONFIRMATION EMAIL ---
    # In development, this prints to console
    # In production, sends real email
    transport_name = booking.get_transport_name()
    route = booking.get_route()
    departure = booking.get_departure_datetime()

    email_subject = f'TravelEase - Booking Confirmed! {booking.booking_reference}'
    email_message = f"""
╔══════════════════════════════════════════╗
║     TRAVELEASE - BOOKING CONFIRMED!      ║
╚══════════════════════════════════════════╝

Booking Reference: {booking.booking_reference}
Status: CONFIRMED ✅

━━━ PASSENGER DETAILS ━━━
Name: {booking.passenger_name}
Email: {booking.passenger_email}
Phone: {booking.passenger_phone}
Seat Number: {booking.seat_number}

━━━ JOURNEY DETAILS ━━━
Transport: {transport_name}
Route: {route}
Departure: {departure}
Booking Type: {booking.booking_type}

━━━ PAYMENT DETAILS ━━━
Amount: NPR {booking.total_price}
Payment Method: {payment_method}
Transaction ID: {payment.transaction_id}
Payment Status: SUCCESS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing TravelEase!
For any queries, contact support@travelease.com

Safe travels! ✈️🚌
"""
    try:
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.passenger_email],
            fail_silently=False,
        )
    except Exception:
        pass  # Email delivery is best-effort; booking is already confirmed

    messages.success(request, f'Payment successful! Booking {booking.booking_reference} confirmed.')
    return redirect('booking:booking_confirmation', booking_id=booking.id)


# =============================================
# PAYMENT FAILURE VIEW (Simulated)
# =============================================
@login_required
def payment_failed(request, booking_id):
    """
    Simulated payment failure page.
    Allows user to retry payment.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        # Create a failed payment record
        Payment.objects.create(
            booking=booking,
            payment_method=request.POST.get('payment_method', 'KHALTI'),
            amount=booking.total_price,
            payment_status='FAILED',
            remarks='Simulated payment failure',
        )
        messages.warning(request, 'Payment simulation: Transaction failed. You can retry.')
        return redirect('payment:make_payment', booking_id=booking.id)

    return render(request, 'payment/payment_failed.html', {'booking': booking})
