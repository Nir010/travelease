"""
TravelEase - Booking Admin
admin.py - Django admin panel configuration for booking models

Registers Bus, Flight, Booking, Payment models in the admin panel.
Customizes how they appear (list display, search, filters, inline images).
"""

from django.contrib import admin
from .models import Bus, BusImage, Flight, FlightImage, Booking, Payment


# =============================================
# BUS IMAGE INLINE
# =============================================
# Inline allows editing BusImage records directly inside the Bus admin page
class BusImageInline(admin.TabularInline):
    model = BusImage
    extra = 3  # Show 3 empty image slots for adding new images
    fields = ['image', 'caption', 'is_primary']


# =============================================
# FLIGHT IMAGE INLINE
# =============================================
class FlightImageInline(admin.TabularInline):
    model = FlightImage
    extra = 3
    fields = ['image', 'caption', 'is_primary']


# =============================================
# BUS ADMIN
# =============================================
@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    """
    Admin configuration for Bus model.

    Features:
    - Search by bus number, name, cities
    - Filter by bus type, departure city, date
    - Inline image management
    - Bulk actions (activate/deactivate)
    """
    # Columns shown in the list view
    list_display = [
        'bus_number', 'bus_name', 'bus_type', 'departure_city',
        'destination_city', 'departure_date', 'departure_time',
        'price', 'available_seats', 'total_seats', 'is_active'
    ]

    # Clickable fields that link to edit page
    list_display_links = ['bus_number', 'bus_name']

    # Searchable fields (admin search box)
    search_fields = [
        'bus_number', 'bus_name', 'departure_city',
        'destination_city', 'departure_date'
    ]

    # Filter sidebar options
    list_filter = [
        'bus_type', 'departure_city', 'destination_city',
        'departure_date', 'is_active'
    ]

    # Default ordering
    ordering = ['departure_date', 'departure_time']

    # Fields organization in edit form
    fieldsets = (
        ('Bus Information', {
            'fields': ('bus_number', 'bus_name', 'bus_type', 'is_active')
        }),
        ('Route Details', {
            'fields': ('departure_city', 'destination_city', 'pickup_point', 'dropoff_point')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time', 'arrival_time', 'duration')
        }),
        ('Seats & Pricing', {
            'fields': ('total_seats', 'available_seats', 'price')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
    )

    # Add inline image edit
    inlines = [BusImageInline]

    # Actions available in dropdown
    actions = ['make_active', 'make_inactive']

    @admin.action(description='Activate selected buses')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected buses')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)


# =============================================
# BUS IMAGE ADMIN
# =============================================
@admin.register(BusImage)
class BusImageAdmin(admin.ModelAdmin):
    list_display = ['bus', 'caption', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary']
    search_fields = ['bus__bus_name', 'caption']


# =============================================
# FLIGHT ADMIN
# =============================================
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        'flight_number', 'airline', 'flight_type', 'departure_city',
        'destination_city', 'departure_date', 'departure_time',
        'price', 'available_seats', 'total_seats', 'is_active'
    ]
    list_display_links = ['flight_number', 'airline']
    search_fields = [
        'flight_number', 'airline', 'departure_city',
        'destination_city', 'departure_date'
    ]
    list_filter = [
        'flight_type', 'departure_city', 'destination_city',
        'departure_date', 'is_active'
    ]
    ordering = ['departure_date', 'departure_time']

    fieldsets = (
        ('Flight Information', {
            'fields': ('flight_number', 'airline', 'flight_type', 'is_active')
        }),
        ('Route Details', {
            'fields': ('departure_city', 'destination_city', 'terminal', 'gate')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time', 'arrival_time', 'duration')
        }),
        ('Seats & Pricing', {
            'fields': ('total_seats', 'available_seats', 'price')
        }),
    )

    inlines = [FlightImageInline]
    actions = ['make_active', 'make_inactive']

    @admin.action(description='Activate selected flights')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected flights')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)


# =============================================
# BOOKING ADMIN
# =============================================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Booking admin - the most important admin view.
    Shows all bookings with payment status.
    """
    list_display = [
        'booking_reference', 'user', 'booking_type',
        'passenger_name', 'seat_number', 'total_price',
        'status', 'booking_date'
    ]
    list_display_links = ['booking_reference', 'passenger_name']
    search_fields = [
        'booking_reference', 'passenger_name', 'passenger_email',
        'seat_number', 'user__username'
    ]
    list_filter = ['booking_type', 'status', 'booking_date']
    ordering = ['-booking_date']
    readonly_fields = ['booking_reference', 'booking_date']

    fieldsets = (
        ('Booking Reference', {
            'fields': ('booking_reference', 'user', 'booking_type', 'status')
        }),
        ('Transport Details', {
            'fields': ('bus', 'flight')
        }),
        ('Passenger Details', {
            'fields': ('passenger_name', 'passenger_email',
                       'passenger_phone', 'passenger_age', 'passenger_gender')
        }),
        ('Booking Details', {
            'fields': ('seat_number', 'number_of_seats', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('booking_date', 'updated_at')
        }),
    )


# =============================================
# PAYMENT ADMIN
# =============================================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'booking_reference_display',
        'payment_method', 'amount', 'payment_status', 'payment_date'
    ]
    search_fields = ['transaction_id', 'booking__booking_reference']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    ordering = ['-payment_date']
    readonly_fields = ['transaction_id', 'payment_date']

    def booking_reference_display(self, obj):
        """Show booking reference in payment list"""
        return obj.booking.booking_reference
    booking_reference_display.short_description = 'Booking Ref'
    booking_reference_display.admin_order_field = 'booking__booking_reference'
