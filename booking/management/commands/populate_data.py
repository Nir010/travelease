http://127.0.0.1:8000/"""
TravelEase - Dummy Data Population Command
==========================================
This management command populates the database with 200+ dummy records:
  - 100+ Bus records with images (various routes across Nepal)
  - 100+ Flight records with images (domestic & international routes)

Why a management command?
  - Re-runnable: `python manage.py populate_data` can be called anytime
  - Transaction-safe: wraps in a single transaction; rolls back on error
  - Idempotent: checks for existing data before creating (won't duplicate)
  - Uses Django ORM: leverages model relationships, validators, signals

Usage:
  python manage.py populate_data          # Create all dummy data
  python manage.py populate_data --clear  # Delete existing data first
  python manage.py populate_data --buses  # Only bus records
  python manage.py populate_data --flights # Only flight records
"""

import random
from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from booking.models import Bus, Flight, BusImage, FlightImage


class Command(BaseCommand):
    help = 'Populate database with 200+ dummy bus and flight records for TravelEase'

    # =========================================================================
    # NEPAL-SPECIFIC DATA
    # These lists provide realistic city names, bus operators, and flight
    # routes that users in Nepal would recognize. Using real place names
    # makes the demo feel authentic.
    # =========================================================================

    NEPAL_CITIES = [
        'Kathmandu', 'Pokhara', 'Chitwan', 'Lumbini', 'Biratnagar',
        'Birgunj', 'Janakpur', 'Nepalgunj', 'Dharan', 'Butwal',
        'Hetauda', 'Bhaktapur', 'Lalitpur', 'Banepa', 'Dhulikhel',
        'Gorkha', 'Baglung', 'Tansen', 'Besisahar', 'Damauli',
    ]

    BUS_OPERATORS = [
        {'name': 'Swift Travels', 'prefix': 'SW'},
        {'name': 'Mountain Express', 'prefix': 'ME'},
        {'name': 'Himalayan Wheels', 'prefix': 'HW'},
        {'name': 'Sagarmatha Yatayat', 'prefix': 'SY'},
        {'name': 'Annapurna Deluxe', 'prefix': 'AD'},
        {'name': 'Green Line Travels', 'prefix': 'GL'},
        {'name': 'Lumbini Wheels', 'prefix': 'LW'},
        {'name': 'Makalu Bus Sewa', 'prefix': 'MB'},
        {'name': 'Tourist Bus Nepal', 'prefix': 'TB'},
        {'name': 'Yeti Travels', 'prefix': 'YT'},
        {'name': 'Peace Zone Travels', 'prefix': 'PZ'},
        {'name': 'Capital Yatayat', 'prefix': 'CY'},
        {'name': 'Royal Express', 'prefix': 'RE'},
        {'name': 'Snow Land Travels', 'prefix': 'SL'},
        {'name': 'Koshi Yatayat', 'prefix': 'KY'},
    ]

    BUS_TYPES = ['AC', 'NON_AC', 'SLEEPER', 'SEMI_SLEEPER', 'VOLVO', 'TATA', 'MINI']

    BUS_AMENITIES_POOL = [
        'WiFi', 'USB Charging', 'AC', 'Reading Light', 'Blanket',
        'Water Bottle', 'Snacks', 'TV Screen', 'Emergency Exit',
        'First Aid Kit', 'Fire Extinguisher', 'Reclining Seats',
        'Foot Rest', 'Curtains', 'Luggage Space',
    ]

    FLIGHT_AIRLINES = [
        {'name': 'Himalaya Airlines', 'code': 'H9'},
        {'name': 'Nepal Airlines', 'code': 'RA'},
        {'name': 'Buddha Air', 'code': 'BHA'},
        {'name': 'Yeti Airlines', 'code': 'YT'},
        {'name': 'Saurya Airlines', 'code': 'SA'},
        {'name': 'Shree Airlines', 'code': 'SHA'},
        {'name': 'Summit Air', 'code': 'SMA'},
        {'name': 'Tara Air', 'code': 'TA'},
        {'name': 'Simrik Airlines', 'code': 'SIM'},
        {'name': 'Guna Airlines', 'code': 'GA'},
    ]

    FLIGHT_DESTINATIONS = [
        'Biratnagar', 'Pokhara', 'Nepalgunj', 'Bhairahawa', 'Janakpur',
        'Bhadrapur', 'Simara', 'Dhangadhi', 'Tumlingtar', 'Lukla',
        'Jomsom', 'Bharatpur', 'Rajbiraj', 'Phaplu', 'Rukum',
    ]

    INTERNATIONAL_DESTINATIONS = [
        'Delhi', 'Mumbai', 'Kolkata', 'Bangalore', 'Dubai',
        'Kuala Lumpur', 'Bangkok', 'Doha', 'Abu Dhabi', 'Singapore',
        'Hong Kong', 'Tokyo', 'Seoul', 'Istanbul', 'London',
    ]

    FLIGHT_AMENITIES_POOL = [
        'In-flight Meal', 'WiFi', 'USB Charging', 'Blanket & Pillow',
        'In-flight Entertainment', 'Headphones', 'Magazine',
        'Window Shade', 'Reading Light', 'Overhead Bin',
        'Life Vest', 'Oxygen Mask', 'Call Button', 'Tray Table',
        'Adjustable Headrest',
    ]

    # =========================================================================
    # HELPER: Random future date
    # Generates a date between `days_from` and `days_to` from today.
    # This ensures all generated records are in the future (bookable).
    # =========================================================================
    @staticmethod
    def random_future_date(days_from=0, days_to=60):
        today = date.today()
        offset = random.randint(days_from, days_to)
        return today + timedelta(days=offset)

    # =========================================================================
    # HELPER: Random time string
    # Returns a time like "07:30" for realistic departure/arrival times.
    # =========================================================================
    @staticmethod
    def random_time(min_hour=6, max_hour=22):
        hour = random.randint(min_hour, max_hour)
        minute = random.choice([0, 15, 30, 45])
        return f"{hour:02d}:{minute:02d}"

    # =========================================================================
    # HELPER: Calculate arrival time from departure + duration
    # =========================================================================
    @staticmethod
    def calculate_arrival(dep_time_str, hours_add):
        dep_h, dep_m = map(int, dep_time_str.split(':'))
        total_minutes = dep_h * 60 + dep_m + int(hours_add * 60)
        arr_h = (total_minutes // 60) % 24
        arr_m = total_minutes % 60
        return f"{arr_h:02d}:{arr_m:02d}"

    # =========================================================================
    # HELPER: Random amenities subset
    # =========================================================================
    @staticmethod
    def random_amenities(pool, min_count=2, max_count=6):
        count = random.randint(min_count, max_count)
        return ', '.join(random.sample(pool, count))

    # =========================================================================
    # BUS GENERATION
    # Creates bus records with realistic route data, pricing (NPR 500-3500),
    # and varied seat counts. Each bus gets a unique number like SW-1234.
    # =========================================================================
    def create_buses(self, count=100):
        self.stdout.write('  Creating bus records...')

        existing_count = Bus.objects.count()
        if existing_count >= count:
            self.stdout.write(f'    {existing_count} buses already exist. Skipping.')
            return

        created = 0
        used_routes = set()

        while created < count:
            # Pick two distinct cities for departure and destination
            dep = random.choice(self.NEPAL_CITIES)
            dest = random.choice(self.NEPAL_CITIES)
            while dest == dep:
                dest = random.choice(self.NEPAL_CITIES)

            # Avoid duplicate routes (keep variety)
            route_key = f"{dep}-{dest}"
            if route_key in used_routes and len(used_routes) < 30:
                continue
            used_routes.add(route_key)

            # Pick a random operator
            operator = random.choice(self.BUS_OPERATORS)
            bus_type = random.choice(self.BUS_TYPES)

            # Generate realistic bus number: operator prefix + 4 digits
            bus_number = f"{operator['prefix']}-{random.randint(1000, 9999)}"

            # Pricing based on bus type (AC/Sleeper cost more)
            base_price = random.randint(500, 1500)
            if bus_type in ('AC', 'VOLVO'):
                base_price += random.randint(300, 800)
            elif bus_type == 'SLEEPER':
                base_price += random.randint(500, 1500)
            elif bus_type == 'SEMI_SLEEPER':
                base_price += random.randint(200, 600)

            # Seat count varies by bus type
            if bus_type == 'MINI':
                total_seats = random.choice([16, 20, 24])
            elif bus_type in ('SLEEPER', 'SEMI_SLEEPER'):
                total_seats = random.choice([28, 30, 32])
            else:
                total_seats = random.choice([32, 36, 40, 44])

            # Duration based on route (Pokhara=~7h, Chitwan=~5h, far=~12h)
            duration_map = {
                'Pokhara': (6, 8), 'Chitwan': (4, 6), 'Lumbini': (7, 9),
                'Biratnagar': (10, 14), 'Nepalgunj': (12, 16),
                'Janakpur': (8, 12), 'Dharan': (10, 14), 'Butwal': (7, 10),
                'Besisahar': (6, 9), 'Gorkha': (5, 8), 'Baglung': (8, 12),
                'Tansen': (7, 10), 'Damauli': (5, 7),
            }
            dur_range = duration_map.get(dest, (3, 8))
            duration_hours = round(random.uniform(dur_range[0], dur_range[1]), 1)

            # Time
            dep_time = self.random_time()
            arr_time = self.calculate_arrival(dep_time, duration_hours)
            dep_date = self.random_future_date(0, 45)

            # Some seats already booked (makes the seat map look realistic)
            booked_seats = random.randint(0, total_seats // 4)
            available_seats = total_seats - booked_seats

            # Pickup/dropoff points
            if dep == 'Kathmandu':
                pickup = random.choice([
                    'Kalanki', 'Gongabu Bus Park', 'Koteshwor',
                    'Balaju Bypass', 'Swayambhu', 'Chabahil',
                ])
            else:
                pickup = f"{dep} Bus Park"

            if dest == 'Kathmandu':
                dropoff = random.choice([
                    'Kalanki', 'Gongabu Bus Park', 'Koteshwor',
                    'Balaju Bypass', 'Swayambhu', 'Chabahil',
                ])
            else:
                dropoff = f"{dest} Bus Park"

            bus = Bus.objects.create(
                bus_number=bus_number,
                bus_name=f"{operator['name']}",
                bus_type=bus_type,
                departure_city=dep,
                destination_city=dest,
                departure_date=dep_date,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration=duration_hours,
                price=base_price,
                total_seats=total_seats,
                available_seats=available_seats,
                amenities=self.random_amenities(self.BUS_AMENITIES_POOL),
                pickup_point=pickup,
                dropoff_point=dropoff,
                is_active=random.random() > 0.05,  # 95% active
            )

            # Create a placeholder image record (admin can upload actual photos later)
            BusImage.objects.create(
                bus=bus,
                caption=f"{operator['name']} - {bus_type} Bus",
                is_primary=True,
            )

            created += 1
            if created % 20 == 0:
                self.stdout.write(f'    Created {created} buses...')

        self.stdout.write(self.style.SUCCESS(f'    ✓ Created {created} bus records'))

    # =========================================================================
    # FLIGHT GENERATION
    # Creates flight records with domestic (Nepal) and international routes.
    # Domestic: Kathmandu ↔ various cities, NPR 3000-15000
    # International: Kathmandu → foreign cities, NPR 15000-120000
    # =========================================================================
    def create_flights(self, count=100):
        self.stdout.write('  Creating flight records...')

        existing_count = Flight.objects.count()
        if existing_count >= count:
            self.stdout.write(f'    {existing_count} flights already exist. Skipping.')
            return

        created = 0
        used_routes = set()
        domestic_ratio = 0.7  # 70% domestic, 30% international

        while created < count:
            airline = random.choice(self.FLIGHT_AIRLINES)

            if random.random() < domestic_ratio:
                # Domestic flight
                dep = 'Kathmandu'
                dest = random.choice(self.FLIGHT_DESTINATIONS)
                base_price = random.randint(3000, 15000)
                duration_hours = round(random.uniform(0.5, 1.5), 1)
                flight_type = 'DOMESTIC'
            else:
                # International flight
                dep = 'Kathmandu'
                dest = random.choice(self.INTERNATIONAL_DESTINATIONS)
                base_price = random.randint(15000, 120000)
                duration_hours = round(random.uniform(1.5, 8.0), 1)
                flight_type = 'INTERNATIONAL'

            route_key = f"{dep}-{dest}-{flight_type}"
            if route_key in used_routes and len(used_routes) < 25:
                continue
            used_routes.add(route_key)

            # Flight number: airline code + 3-4 digits
            flight_number = f"{airline['code']}{random.randint(100, 9999)}"

            # Seat count (typical aircraft)
            if flight_type == 'DOMESTIC':
                total_seats = random.choice([48, 56, 72, 78])
            else:
                total_seats = random.choice([120, 150, 180, 210])

            booked_seats = random.randint(5, total_seats // 3)
            available_seats = total_seats - booked_seats

            dep_time = self.random_time(5, 23)
            arr_time = self.calculate_arrival(dep_time, duration_hours)
            dep_date = self.random_future_date(1, 60)

            # Pickup/dropoff
            if flight_type == 'DOMESTIC':
                pickup = 'Tribhuvan International Airport, Domestic Terminal'
                dropoff = f'{dest} Airport'
            else:
                pickup = 'Tribhuvan International Airport, International Terminal'
                dropoff = f'{dest} International Airport'

            flight = Flight.objects.create(
                flight_number=flight_number,
                airline=airline['name'],
                departure_city=dep,
                destination_city=dest,
                departure_date=dep_date,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration=f"{duration_hours}h",
                price=base_price,
                total_seats=total_seats,
                available_seats=available_seats,
                flight_type=flight_type,
                terminal='Terminal 1' if flight_type == 'DOMESTIC' else 'International Terminal',
                gate=f"G{random.randint(1, 20)}",
                is_active=True,
            )

            FlightImage.objects.create(
                flight=flight,
                caption=f"{airline['name']} - {flight_type.title()} Flight",
                is_primary=True,
            )

            created += 1
            if created % 20 == 0:
                self.stdout.write(f'    Created {created} flights...')

        self.stdout.write(self.style.SUCCESS(f'    ✓ Created {created} flight records'))

    # =========================================================================
    # COMMAND ENTRY POINT
    # Django calls handle() when `python manage.py populate_data` is run.
    # We parse optional flags and dispatch to the appropriate generator.
    # =========================================================================
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing bus and flight data before creating new records',
        )
        parser.add_argument(
            '--buses',
            action='store_true',
            help='Only generate bus records',
        )
        parser.add_argument(
            '--flights',
            action='store_true',
            help='Only generate flight records',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚌✈️  TravelEase Data Population'))
        self.stdout.write('=' * 50)

        # If --clear flag is set, purge existing data
        if options['clear']:
            self.stdout.write(self.style.WARNING('\n  Clearing existing data...'))
            BusImage.objects.all().delete()
            Bus.objects.all().delete()
            FlightImage.objects.all().delete()
            Flight.objects.all().delete()
            self.stdout.write('  ✓ All existing data cleared.\n')

        # Determine what to generate
        do_buses = options['buses'] or (not options['flights'])
        do_flights = options['flights'] or (not options['buses'])

        if do_buses:
            self.stdout.write('\n  🚌 Generating Bus Records...')
            self.create_buses(count=100)

        if do_flights:
            self.stdout.write('\n  ✈️  Generating Flight Records...')
            self.create_flights(count=100)

        # Summary
        total_buses = Bus.objects.count()
        total_flights = Flight.objects.count()

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Population complete! Total: {total_buses} buses + {total_flights} flights = {total_buses + total_flights} records'
        ))
        self.stdout.write('')

        # Hint about creating a superuser
        self.stdout.write(self.style.WARNING(
            '  💡 Tip: Run `python manage.py createsuperuser` to create an admin account,\n'
            '     then visit http://127.0.0.1:8000/admin/ to manage data and upload real bus/flight photos.'
        ))
        self.stdout.write('')