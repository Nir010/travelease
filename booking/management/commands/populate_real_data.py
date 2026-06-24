"""
TravelEase - Realistic Nepal Bus & Flight Data
==============================================
Populates the database with realistic data based on actual:
  - Nepal bus operators (Green Line, Yeti, Sajha, etc.)
  - Real routes with accurate departure times & fares
  - Domestic/international flights from TIA (Kathmandu)
  - Real airline names (Buddha Air, Yeti Airlines, etc.)

Usage:
  python manage.py populate_real_data
  python manage.py populate_real_data --clear
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from booking.models import Bus, Flight
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with realistic Nepal bus and flight data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Bus.objects.all().delete()
            Flight.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        self.stdout.write(self.style.WARNING('\n🚌✈️  TravelEase — Realistic Nepal Data\n' + '=' * 50))
        self.create_buses()
        self.create_flights()
        self.stdout.write(self.style.SUCCESS('\n✅ Done! Real Nepal routes loaded.\n'))

    # ------------------------------------------------------------------
    # BUS DATA
    # ------------------------------------------------------------------
    def create_buses(self):
        self.stdout.write('\n  🚌 Creating Bus Records...')

        # Each entry: (operator, bus_number, bus_type, from, to, dep_time, arr_time, duration, price, seats, pickup, dropoff, amenities)
        bus_data = [
            # ── KATHMANDU → POKHARA ──
            ('Green Line Travels',   'GL-001', 'AC',         'Kathmandu', 'Pokhara',    '07:00', '14:00', '7 hrs',   1800, 42, 'Sundhara, Kathmandu',  'Pokhara Bus Park',       'AC,WiFi,USB Charging,Water Bottle,Reclining Seats'),
            ('Green Line Travels',   'GL-002', 'AC',         'Kathmandu', 'Pokhara',    '08:30', '15:30', '7 hrs',   1800, 42, 'Sundhara, Kathmandu',  'Pokhara Bus Park',       'AC,WiFi,USB Charging,Water Bottle,Reclining Seats'),
            ('Yeti Travels',         'YT-011', 'VOLVO',      'Kathmandu', 'Pokhara',    '06:30', '13:00', '6.5 hrs', 2200, 40, 'Kalanki, Kathmandu',   'Pokhara Lakeside',       'AC,WiFi,USB Charging,Blanket,Water Bottle,TV Screen,Reclining Seats'),
            ('Yeti Travels',         'YT-012', 'VOLVO',      'Kathmandu', 'Pokhara',    '19:00', '01:30', '6.5 hrs', 2200, 40, 'Kalanki, Kathmandu',   'Pokhara Lakeside',       'AC,WiFi,USB Charging,Blanket,Water Bottle,TV Screen,Reclining Seats'),
            ('Sajha Yatayat',        'SJ-021', 'AC',         'Kathmandu', 'Pokhara',    '07:30', '14:30', '7 hrs',   1400, 45, 'Ratnapark, Kathmandu', 'Pokhara Bus Park',       'AC,USB Charging,Water Bottle'),
            ('Sajha Yatayat',        'SJ-022', 'AC',         'Kathmandu', 'Pokhara',    '09:00', '16:00', '7 hrs',   1400, 45, 'Ratnapark, Kathmandu', 'Pokhara Bus Park',       'AC,USB Charging,Water Bottle'),
            ('Prithvi Deluxe',       'PD-031', 'SEMI_SLEEPER','Kathmandu','Pokhara',    '20:00', '03:00', '7 hrs',   1600, 38, 'Gongabu Bus Park',     'Pokhara Bus Park',       'AC,Reclining Seats,Blanket,USB Charging'),
            ('Mustang Travels',      'MT-041', 'NON_AC',     'Kathmandu', 'Pokhara',    '06:00', '13:30', '7.5 hrs', 900,  48, 'Gongabu Bus Park',     'Pokhara Bus Park',       'Water Bottle,Emergency Exit'),
            ('Tourist Bus Nepal',    'TB-051', 'VOLVO',      'Kathmandu', 'Pokhara',    '08:00', '14:00', '6 hrs',   2500, 40, 'Thamel, Kathmandu',    'Pokhara Lakeside',       'AC,WiFi,USB Charging,Blanket,Snacks,TV Screen,Reclining Seats'),
            ('Adventure Bus Nepal',  'AB-061', 'AC',         'Kathmandu', 'Pokhara',    '07:00', '14:00', '7 hrs',   1700, 42, 'Ratnapark, Kathmandu', 'Pokhara Bus Park',       'AC,USB Charging,Water Bottle,Reclining Seats'),

            # ── POKHARA → KATHMANDU ──
            ('Green Line Travels',   'GL-101', 'AC',         'Pokhara', 'Kathmandu',   '07:00', '14:00', '7 hrs',   1800, 42, 'Pokhara Bus Park',     'Sundhara, Kathmandu',   'AC,WiFi,USB Charging,Water Bottle,Reclining Seats'),
            ('Yeti Travels',         'YT-111', 'VOLVO',      'Pokhara', 'Kathmandu',   '07:00', '13:30', '6.5 hrs', 2200, 40, 'Pokhara Lakeside',     'Kalanki, Kathmandu',    'AC,WiFi,USB Charging,Blanket,Water Bottle,TV Screen,Reclining Seats'),
            ('Sajha Yatayat',        'SJ-121', 'AC',         'Pokhara', 'Kathmandu',   '07:30', '14:30', '7 hrs',   1400, 45, 'Pokhara Bus Park',     'Ratnapark, Kathmandu',  'AC,USB Charging,Water Bottle'),
            ('Tourist Bus Nepal',    'TB-131', 'VOLVO',      'Pokhara', 'Kathmandu',   '08:00', '14:00', '6 hrs',   2500, 40, 'Pokhara Lakeside',     'Thamel, Kathmandu',     'AC,WiFi,USB Charging,Blanket,Snacks,TV Screen,Reclining Seats'),
            ('Mustang Travels',      'MT-141', 'NON_AC',     'Pokhara', 'Kathmandu',   '06:30', '14:00', '7.5 hrs', 900,  48, 'Pokhara Bus Park',     'Gongabu Bus Park',      'Water Bottle,Emergency Exit'),

            # ── KATHMANDU → CHITWAN ──
            ('Green Line Travels',   'GL-201', 'AC',         'Kathmandu', 'Chitwan',    '07:00', '11:30', '4.5 hrs', 1200, 42, 'Sundhara, Kathmandu',  'Sauraha, Chitwan',       'AC,WiFi,USB Charging,Water Bottle,Reclining Seats'),
            ('Yeti Travels',         'YT-211', 'VOLVO',      'Kathmandu', 'Chitwan',    '06:30', '10:30', '4 hrs',   1600, 40, 'Kalanki, Kathmandu',   'Bharatpur, Chitwan',     'AC,WiFi,USB Charging,Blanket,Water Bottle,TV Screen'),
            ('Sajha Yatayat',        'SJ-221', 'AC',         'Kathmandu', 'Chitwan',    '08:00', '12:30', '4.5 hrs', 900,  45, 'Gongabu Bus Park',     'Bharatpur, Chitwan',     'AC,USB Charging,Water Bottle'),
            ('Himalayan Travels',    'HT-231', 'NON_AC',     'Kathmandu', 'Chitwan',    '06:00', '11:00', '5 hrs',   700,  50, 'Gongabu Bus Park',     'Narayanghat, Chitwan',   'Emergency Exit,Water Bottle'),
            ('Nature View Bus',      'NV-241', 'SEMI_SLEEPER','Kathmandu','Chitwan',    '20:30', '01:00', '4.5 hrs', 1100, 38, 'Kalanki, Kathmandu',   'Sauraha, Chitwan',       'AC,Reclining Seats,Blanket'),

            # ── CHITWAN → KATHMANDU ──
            ('Green Line Travels',   'GL-301', 'AC',         'Chitwan', 'Kathmandu',   '07:00', '11:30', '4.5 hrs', 1200, 42, 'Sauraha, Chitwan',     'Sundhara, Kathmandu',   'AC,WiFi,USB Charging,Water Bottle,Reclining Seats'),
            ('Yeti Travels',         'YT-311', 'VOLVO',      'Chitwan', 'Kathmandu',   '07:00', '11:00', '4 hrs',   1600, 40, 'Bharatpur, Chitwan',   'Kalanki, Kathmandu',    'AC,WiFi,USB Charging,Blanket,Water Bottle,TV Screen'),
            ('Sajha Yatayat',        'SJ-321', 'AC',         'Chitwan', 'Kathmandu',   '08:00', '12:30', '4.5 hrs', 900,  45, 'Bharatpur, Chitwan',   'Gongabu Bus Park',      'AC,USB Charging,Water Bottle'),

            # ── KATHMANDU → BUTWAL ──
            ('Lumbini Express',      'LE-401', 'AC',         'Kathmandu', 'Butwal',     '07:00', '13:00', '6 hrs',   1300, 44, 'Gongabu Bus Park',     'Butwal Bus Park',        'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Siddhartha Travels',   'ST-411', 'SEMI_SLEEPER','Kathmandu','Butwal',     '20:00', '02:30', '6.5 hrs', 1400, 38, 'Kalanki, Kathmandu',   'Butwal Bus Park',        'AC,Blanket,Reclining Seats,USB Charging'),
            ('Peace Zone Travels',   'PZ-421', 'AC',         'Kathmandu', 'Butwal',     '07:30', '13:30', '6 hrs',   1200, 42, 'Gongabu Bus Park',     'Butwal Bus Park',        'AC,USB Charging,Water Bottle'),
            ('Lumbini Deluxe',       'LD-431', 'VOLVO',      'Kathmandu', 'Butwal',     '19:30', '01:30', '6 hrs',   2000, 40, 'Kalanki, Kathmandu',   'Butwal Bus Park',        'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),

            # ── KATHMANDU → BIRATNAGAR ──
            ('Koshi Express',        'KE-501', 'AC',         'Kathmandu', 'Biratnagar', '07:00', '18:00', '11 hrs',  1800, 44, 'Gongabu Bus Park',     'Biratnagar Bus Park',    'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Koshi Express',        'KE-502', 'SLEEPER',    'Kathmandu', 'Biratnagar', '18:00', '05:00', '11 hrs',  2200, 36, 'Gongabu Bus Park',     'Biratnagar Bus Park',    'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Eastern Travels',      'ET-511', 'SEMI_SLEEPER','Kathmandu','Biratnagar', '17:30', '04:30', '11 hrs',  1900, 38, 'Kalanki, Kathmandu',   'Biratnagar Bus Park',    'AC,Blanket,Reclining Seats'),
            ('Himalayan Express',    'HE-521', 'NON_AC',     'Kathmandu', 'Biratnagar', '06:30', '17:30', '11 hrs',  1100, 50, 'Gongabu Bus Park',     'Biratnagar Bus Park',    'Water Bottle,Emergency Exit'),

            # ── KATHMANDU → BIRGUNJ ──
            ('Bagmati Express',      'BE-601', 'AC',         'Kathmandu', 'Birgunj',    '07:00', '12:30', '5.5 hrs', 1000, 44, 'Gongabu Bus Park',     'Birgunj Bus Park',       'AC,USB Charging,Water Bottle'),
            ('Border Express',       'BX-611', 'VOLVO',      'Kathmandu', 'Birgunj',    '06:30', '12:00', '5.5 hrs', 1500, 40, 'Kalanki, Kathmandu',   'Birgunj Bus Park',       'AC,WiFi,USB Charging,Water Bottle,TV Screen'),
            ('Narayani Yatayat',     'NY-621', 'NON_AC',     'Kathmandu', 'Birgunj',    '06:00', '12:00', '6 hrs',   700,  50, 'Gongabu Bus Park',     'Birgunj Bus Park',       'Water Bottle,Emergency Exit'),

            # ── KATHMANDU → JANAKPUR ──
            ('Mithila Express',      'MI-701', 'AC',         'Kathmandu', 'Janakpur',   '07:00', '14:00', '7 hrs',   1200, 44, 'Gongabu Bus Park',     'Janakpur Bus Park',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Janaki Travels',       'JT-711', 'SEMI_SLEEPER','Kathmandu','Janakpur',   '19:00', '02:00', '7 hrs',   1400, 38, 'Kalanki, Kathmandu',   'Janakpur Bus Park',      'AC,Blanket,Reclining Seats'),

            # ── KATHMANDU → NEPALGUNJ ──
            ('Bheri Express',        'BH-801', 'VOLVO',      'Kathmandu', 'Nepalgunj',  '18:00', '07:00', '13 hrs',  2500, 40, 'Gongabu Bus Park',     'Nepalgunj Bus Park',     'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Mid-West Travels',     'MW-811', 'SLEEPER',    'Kathmandu', 'Nepalgunj',  '17:30', '06:30', '13 hrs',  2200, 36, 'Kalanki, Kathmandu',   'Nepalgunj Bus Park',     'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Surkhet Bus Sewa',     'SB-821', 'NON_AC',     'Kathmandu', 'Nepalgunj',  '06:30', '19:30', '13 hrs',  1400, 50, 'Gongabu Bus Park',     'Nepalgunj Bus Park',     'Water Bottle,Emergency Exit'),

            # ── POKHARA → CHITWAN ──
            ('Prithvi Travels',      'PT-901', 'AC',         'Pokhara', 'Chitwan',     '07:00', '11:00', '4 hrs',   900,  44, 'Pokhara Bus Park',     'Bharatpur, Chitwan',    'AC,USB Charging,Water Bottle'),
            ('Lake City Express',    'LC-911', 'NON_AC',     'Pokhara', 'Chitwan',     '06:30', '11:00', '4.5 hrs', 600,  50, 'Pokhara Bus Park',     'Narayanghat, Chitwan',  'Water Bottle,Emergency Exit'),

            # ── POKHARA → BUTWAL ──
            ('Gandaki Yatayat',      'GY-951', 'AC',         'Pokhara', 'Butwal',      '07:30', '12:00', '4.5 hrs', 900,  44, 'Pokhara Bus Park',     'Butwal Bus Park',       'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Lumbini Express',      'LE-961', 'NON_AC',     'Pokhara', 'Butwal',      '07:00', '12:00', '5 hrs',   600,  50, 'Pokhara Bus Park',     'Butwal Bus Park',       'Water Bottle,Emergency Exit'),

            # ── DHARAN → KATHMANDU ──
            ('Koshi Yatayat',        'KO-A01', 'AC',         'Dharan', 'Kathmandu',   '07:00', '18:00', '11 hrs',  1700, 44, 'Dharan Bus Park',      'Gongabu Bus Park',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Koshi Yatayat',        'KO-A02', 'SLEEPER',    'Dharan', 'Kathmandu',   '17:00', '04:00', '11 hrs',  2100, 36, 'Dharan Bus Park',      'Gongabu Bus Park',      'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),

            # ── KATHMANDU → DHARAN ──
            ('Eastern Express',      'EX-B01', 'AC',         'Kathmandu', 'Dharan',    '07:00', '18:00', '11 hrs',  1700, 44, 'Gongabu Bus Park',     'Dharan Bus Park',        'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Eastern Express',      'EX-B02', 'SLEEPER',    'Kathmandu', 'Dharan',    '17:30', '04:30', '11 hrs',  2100, 36, 'Gongabu Bus Park',     'Dharan Bus Park',        'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),

            # ── KATHMANDU → LUMBINI ──
            ('Rupandehi Express',    'RE-C01', 'AC',         'Kathmandu', 'Lumbini',   '07:00', '14:00', '7 hrs',   1300, 44, 'Gongabu Bus Park',     'Lumbini Bus Park',       'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Buddha Land Travels',  'BL-C11', 'VOLVO',      'Kathmandu', 'Lumbini',   '19:30', '02:30', '7 hrs',   2000, 40, 'Kalanki, Kathmandu',   'Lumbini Bus Park',       'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),

            # ── BUTWAL → KATHMANDU ──
            ('Lumbini Express',      'LE-D01', 'AC',         'Butwal', 'Kathmandu',   '07:00', '13:00', '6 hrs',   1300, 44, 'Butwal Bus Park',      'Gongabu Bus Park',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Siddhartha Travels',   'ST-D11', 'VOLVO',      'Butwal', 'Kathmandu',   '19:30', '01:30', '6 hrs',   2000, 40, 'Butwal Bus Park',      'Kalanki, Kathmandu',    'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
        ]

        today = date.today()
        created = 0

        for operator, number, btype, from_city, to_city, dep_t, arr_t, duration, price, seats, pickup, dropoff, amenities in bus_data:
            for day_offset in range(7):
                travel_date = today + timedelta(days=day_offset)
                bus_num = f"{number}-{travel_date.strftime('%d%m')}"

                if Bus.objects.filter(bus_number=bus_num).exists():
                    continue

                avail = random.randint(max(1, seats - random.randint(0, seats // 2)), seats)
                Bus.objects.create(
                    bus_number=bus_num,
                    bus_name=operator,
                    bus_type=btype,
                    departure_city=from_city,
                    destination_city=to_city,
                    departure_date=travel_date,
                    departure_time=dep_t,
                    arrival_time=arr_t,
                    duration=duration,
                    price=price,
                    total_seats=seats,
                    available_seats=avail,
                    amenities=amenities,
                    pickup_point=pickup,
                    dropoff_point=dropoff,
                    is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'    ✓ Created {created} bus records (7 days of service)'))

    # ------------------------------------------------------------------
    # FLIGHT DATA
    # ------------------------------------------------------------------
    def create_flights(self):
        self.stdout.write('\n  ✈️  Creating Flight Records...')

        # (flight_number, airline, type, from, to, dep_time, arr_time, duration, price, seats, terminal, gate)
        flight_data = [
            # ── DOMESTIC — KATHMANDU → POKHARA ──
            ('U4-101', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '06:00', '06:25', '25 min',  5500,  72,  'Terminal 1', 'Gate 3'),
            ('U4-103', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '09:15', '09:40', '25 min',  5500,  72,  'Terminal 1', 'Gate 3'),
            ('U4-105', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '12:30', '12:55', '25 min',  5500,  72,  'Terminal 1', 'Gate 4'),
            ('U4-107', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '16:00', '16:25', '25 min',  5500,  72,  'Terminal 1', 'Gate 4'),
            ('YT-201', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Pokhara',    '07:30', '07:55', '25 min',  5200,  68,  'Terminal 1', 'Gate 1'),
            ('YT-203', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Pokhara',    '11:00', '11:25', '25 min',  5200,  68,  'Terminal 1', 'Gate 2'),
            ('YT-205', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Pokhara',    '14:30', '14:55', '25 min',  5200,  68,  'Terminal 1', 'Gate 2'),
            ('SH-301', 'Shree Airlines','DOMESTIC', 'Kathmandu', 'Pokhara',    '08:00', '08:25', '25 min',  4800,  56,  'Terminal 1', 'Gate 5'),
            ('SH-303', 'Shree Airlines','DOMESTIC', 'Kathmandu', 'Pokhara',    '13:00', '13:25', '25 min',  4800,  56,  'Terminal 1', 'Gate 5'),
            ('SA-401', 'Saurya Airlines','DOMESTIC','Kathmandu', 'Pokhara',    '09:00', '09:25', '25 min',  4500,  50,  'Terminal 1', 'Gate 6'),

            # ── DOMESTIC — POKHARA → KATHMANDU ──
            ('U4-102', 'Buddha Air',    'DOMESTIC', 'Pokhara', 'Kathmandu',   '07:15', '07:40', '25 min',  5500,  72,  'Terminal 1', 'Gate 1'),
            ('U4-104', 'Buddha Air',    'DOMESTIC', 'Pokhara', 'Kathmandu',   '10:30', '10:55', '25 min',  5500,  72,  'Terminal 1', 'Gate 1'),
            ('U4-106', 'Buddha Air',    'DOMESTIC', 'Pokhara', 'Kathmandu',   '13:45', '14:10', '25 min',  5500,  72,  'Terminal 1', 'Gate 2'),
            ('YT-202', 'Yeti Airlines', 'DOMESTIC', 'Pokhara', 'Kathmandu',   '08:45', '09:10', '25 min',  5200,  68,  'Terminal 1', 'Gate 3'),
            ('YT-204', 'Yeti Airlines', 'DOMESTIC', 'Pokhara', 'Kathmandu',   '12:15', '12:40', '25 min',  5200,  68,  'Terminal 1', 'Gate 3'),
            ('SH-302', 'Shree Airlines','DOMESTIC', 'Pokhara', 'Kathmandu',   '09:15', '09:40', '25 min',  4800,  56,  'Terminal 1', 'Gate 4'),

            # ── DOMESTIC — KATHMANDU → BIRATNAGAR ──
            ('U4-501', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Biratnagar', '07:00', '07:40', '40 min',  7500,  72,  'Terminal 1', 'Gate 7'),
            ('U4-503', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Biratnagar', '10:30', '11:10', '40 min',  7500,  72,  'Terminal 1', 'Gate 7'),
            ('YT-511', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Biratnagar', '08:00', '08:40', '40 min',  7200,  68,  'Terminal 1', 'Gate 8'),
            ('SH-521', 'Shree Airlines','DOMESTIC', 'Kathmandu', 'Biratnagar', '09:15', '09:55', '40 min',  6800,  56,  'Terminal 1', 'Gate 8'),

            # ── DOMESTIC — BIRATNAGAR → KATHMANDU ──
            ('U4-502', 'Buddha Air',    'DOMESTIC', 'Biratnagar', 'Kathmandu', '08:30', '09:10', '40 min',  7500,  72,  'Terminal 1', 'Gate 1'),
            ('YT-512', 'Yeti Airlines', 'DOMESTIC', 'Biratnagar', 'Kathmandu', '09:30', '10:10', '40 min',  7200,  68,  'Terminal 1', 'Gate 2'),

            # ── DOMESTIC — KATHMANDU → NEPALGUNJ ──
            ('U4-601', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Nepalgunj',  '08:00', '09:10', '1 hr 10 min', 10500, 72, 'Terminal 1', 'Gate 9'),
            ('YT-611', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Nepalgunj',  '09:30', '10:40', '1 hr 10 min', 10200, 68, 'Terminal 1', 'Gate 9'),
            ('SH-621', 'Shree Airlines','DOMESTIC', 'Kathmandu', 'Nepalgunj',  '11:00', '12:10', '1 hr 10 min', 9800,  56, 'Terminal 1', 'Gate 10'),

            # ── DOMESTIC — NEPALGUNJ → KATHMANDU ──
            ('U4-602', 'Buddha Air',    'DOMESTIC', 'Nepalgunj', 'Kathmandu',  '10:00', '11:10', '1 hr 10 min', 10500, 72, 'Terminal 1', 'Gate 1'),
            ('YT-612', 'Yeti Airlines', 'DOMESTIC', 'Nepalgunj', 'Kathmandu',  '11:30', '12:40', '1 hr 10 min', 10200, 68, 'Terminal 1', 'Gate 2'),

            # ── DOMESTIC — KATHMANDU → JANAKPUR ──
            ('U4-701', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Janakpur',   '07:30', '08:05', '35 min',  6500,  72,  'Terminal 1', 'Gate 11'),
            ('YT-711', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Janakpur',   '09:00', '09:35', '35 min',  6200,  68,  'Terminal 1', 'Gate 11'),

            # ── DOMESTIC — JANAKPUR → KATHMANDU ──
            ('U4-702', 'Buddha Air',    'DOMESTIC', 'Janakpur', 'Kathmandu',   '09:00', '09:35', '35 min',  6500,  72,  'Terminal 1', 'Gate 1'),
            ('YT-712', 'Yeti Airlines', 'DOMESTIC', 'Janakpur', 'Kathmandu',   '10:30', '11:05', '35 min',  6200,  68,  'Terminal 1', 'Gate 2'),

            # ── DOMESTIC — KATHMANDU → DHANGADHI ──
            ('U4-801', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Dhangadhi',  '09:00', '10:25', '1 hr 25 min', 12000, 72, 'Terminal 1', 'Gate 12'),
            ('YT-811', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Dhangadhi',  '10:30', '11:55', '1 hr 25 min', 11500, 68, 'Terminal 1', 'Gate 12'),

            # ── INTERNATIONAL — KATHMANDU → DELHI ──
            ('AI-901', 'Air India',         'INTERNATIONAL', 'Kathmandu', 'Delhi',     '08:00', '10:30', '2 hrs 30 min',  18000, 156, 'Terminal 2', 'Gate A1'),
            ('AI-903', 'Air India',         'INTERNATIONAL', 'Kathmandu', 'Delhi',     '15:00', '17:30', '2 hrs 30 min',  18000, 156, 'Terminal 2', 'Gate A1'),
            ('6E-911', 'IndiGo',            'INTERNATIONAL', 'Kathmandu', 'Delhi',     '09:30', '12:00', '2 hrs 30 min',  16000, 180, 'Terminal 2', 'Gate A2'),
            ('6E-913', 'IndiGo',            'INTERNATIONAL', 'Kathmandu', 'Delhi',     '16:30', '19:00', '2 hrs 30 min',  16000, 180, 'Terminal 2', 'Gate A2'),
            ('RA-921', 'Nepal Airlines',    'INTERNATIONAL', 'Kathmandu', 'Delhi',     '10:00', '12:30', '2 hrs 30 min',  17500, 140, 'Terminal 2', 'Gate A3'),

            # ── INTERNATIONAL — KATHMANDU → DUBAI ──
            ('EK-A01', 'Emirates',          'INTERNATIONAL', 'Kathmandu', 'Dubai',     '02:15', '05:45', '5 hrs 30 min',  55000, 300, 'Terminal 2', 'Gate B1'),
            ('FZ-A11', 'Flydubai',          'INTERNATIONAL', 'Kathmandu', 'Dubai',     '23:55', '03:25', '5 hrs 30 min',  42000, 189, 'Terminal 2', 'Gate B2'),
            ('RA-A21', 'Nepal Airlines',    'INTERNATIONAL', 'Kathmandu', 'Dubai',     '01:30', '05:00', '5 hrs 30 min',  48000, 140, 'Terminal 2', 'Gate B3'),

            # ── INTERNATIONAL — KATHMANDU → DOHA ──
            ('QR-B01', 'Qatar Airways',     'INTERNATIONAL', 'Kathmandu', 'Doha',      '03:00', '07:00', '5 hrs',         60000, 300, 'Terminal 2', 'Gate C1'),
            ('QR-B03', 'Qatar Airways',     'INTERNATIONAL', 'Kathmandu', 'Doha',      '22:00', '02:00', '5 hrs',         60000, 300, 'Terminal 2', 'Gate C1'),

            # ── INTERNATIONAL — KATHMANDU → KUALA LUMPUR ──
            ('MH-C01', 'Malaysia Airlines', 'INTERNATIONAL', 'Kathmandu', 'Kuala Lumpur', '00:30', '08:30', '5 hrs',      52000, 300, 'Terminal 2', 'Gate D1'),
            ('AK-C11', 'AirAsia',           'INTERNATIONAL', 'Kathmandu', 'Kuala Lumpur', '02:00', '10:00', '5 hrs',      38000, 180, 'Terminal 2', 'Gate D2'),

            # ── INTERNATIONAL — KATHMANDU → BANGKOK ──
            ('TG-D01', 'Thai Airways',      'INTERNATIONAL', 'Kathmandu', 'Bangkok',   '01:00', '06:30', '3 hrs 30 min',  45000, 300, 'Terminal 2', 'Gate E1'),
            ('FD-D11', 'Thai AirAsia',      'INTERNATIONAL', 'Kathmandu', 'Bangkok',   '23:30', '05:00', '3 hrs 30 min',  32000, 180, 'Terminal 2', 'Gate E2'),

            # ── INTERNATIONAL — KATHMANDU → SINGAPORE ──
            ('SQ-E01', 'Singapore Airlines','INTERNATIONAL', 'Kathmandu', 'Singapore', '00:45', '07:45', '4 hrs',         70000, 280, 'Terminal 2', 'Gate F1'),
            ('TR-E11', 'Scoot',             'INTERNATIONAL', 'Kathmandu', 'Singapore', '02:30', '09:30', '4 hrs',         40000, 180, 'Terminal 2', 'Gate F2'),
        ]

        today = date.today()
        created = 0

        for f_num, airline, f_type, from_city, to_city, dep_t, arr_t, duration, price, seats, terminal, gate in flight_data:
            for day_offset in range(7):
                travel_date = today + timedelta(days=day_offset)
                flight_num = f"{f_num}-{travel_date.strftime('%d%m')}"

                if Flight.objects.filter(flight_number=flight_num).exists():
                    continue

                avail = random.randint(max(1, seats - random.randint(0, seats // 3)), seats)
                Flight.objects.create(
                    flight_number=flight_num,
                    airline=airline,
                    flight_type=f_type,
                    departure_city=from_city,
                    destination_city=to_city,
                    departure_date=travel_date,
                    departure_time=dep_t,
                    arrival_time=arr_t,
                    duration=duration,
                    price=price,
                    total_seats=seats,
                    available_seats=avail,
                    terminal=terminal,
                    gate=gate,
                    is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'    ✓ Created {created} flight records (7 days of service)'))
