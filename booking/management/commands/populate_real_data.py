"""
TravelEase - Realistic Nepal Bus & Flight Data (~200 records, 3-day window)
===========================================================================
Buses named after their regional origin/destination — authentic Nepal pattern.
e.g. Kathmandu → Waling  →  "Syangja Gandaki Yatayat"
     Kathmandu → Pokhara →  "Gandaki Express / Annapurna Deluxe"

Usage:
  python manage.py populate_real_data
  python manage.py populate_real_data --clear
"""

from django.core.management.base import BaseCommand
from booking.models import Bus, Flight
from datetime import date, timedelta
import random


DAYS = 3   # generate records for today + 2 more days → ~200 total records


class Command(BaseCommand):
    help = 'Populate database with ~200 realistic Nepal bus and flight records'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            Bus.objects.all().delete()
            Flight.objects.all().delete()
            self.stdout.write('Existing data cleared.')

        self.stdout.write(self.style.WARNING('\n🚌✈️  TravelEase — Nepal Data (~200 records)\n' + '=' * 50))
        self.create_buses()
        self.create_flights()
        total = Bus.objects.count() + Flight.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! {total} records total.\n'))

    # ------------------------------------------------------------------
    # BUS ROUTES  (~34 unique routes × 3 days = ~102 bus records)
    # ------------------------------------------------------------------
    def create_buses(self):
        self.stdout.write('\n  🚌 Creating Bus Records...')

        # (bus_name, prefix, type, from, to, dep, arr, duration, price, seats, pickup, dropoff, amenities)
        routes = [
            # Kathmandu → Pokhara
            ('Gandaki Express',         'GE1', 'AC',           'Kathmandu', 'Pokhara',        '06:30', '13:30', '7 hrs',      1800, 42, 'Gongabu Bus Park, Kathmandu',  'Pokhara Bus Park',            'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Annapurna Deluxe',        'AN1', 'VOLVO',        'Kathmandu', 'Pokhara',        '07:00', '13:30', '6.5 hrs',    2400, 40, 'Kalanki, Kathmandu',           'Pokhara Lakeside',            'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Kaligandaki Yatayat',     'KG1', 'NON_AC',       'Kathmandu', 'Pokhara',        '06:00', '13:30', '7.5 hrs',    900,  50, 'Gongabu Bus Park, Kathmandu',  'Pokhara Bus Park',            'Water Bottle,Emergency Exit'),
            # Pokhara → Kathmandu
            ('Gandaki Express',         'GE2', 'AC',           'Pokhara',   'Kathmandu',      '07:00', '14:00', '7 hrs',      1800, 42, 'Pokhara Bus Park',             'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Annapurna Deluxe',        'AN2', 'VOLVO',        'Pokhara',   'Kathmandu',      '07:00', '13:30', '6.5 hrs',    2400, 40, 'Pokhara Lakeside',             'Kalanki, Kathmandu',          'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            # Kathmandu → Waling / Syangja
            ('Syangja Gandaki Yatayat', 'SG1', 'AC',           'Kathmandu', 'Waling',         '07:00', '15:00', '8 hrs',      1500, 44, 'Gongabu Bus Park, Kathmandu',  'Waling Bus Park, Syangja',    'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Syangja Gandaki Yatayat', 'SG2', 'SEMI_SLEEPER', 'Kathmandu', 'Waling',         '20:30', '04:30', '8 hrs',      1700, 38, 'Kalanki, Kathmandu',           'Waling Bus Park, Syangja',    'AC,Blanket,Reclining Seats,USB Charging'),
            ('Syangja Express',         'SE1', 'AC',           'Kathmandu', 'Syangja',        '07:00', '15:30', '8.5 hrs',    1500, 44, 'Gongabu Bus Park, Kathmandu',  'Syangja Bus Park',            'AC,USB Charging,Water Bottle'),
            # Waling → Kathmandu
            ('Syangja Gandaki Yatayat', 'SG3', 'AC',           'Waling',    'Kathmandu',      '06:00', '14:00', '8 hrs',      1500, 44, 'Waling Bus Park, Syangja',     'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Kathmandu → Chitwan
            ('Narayani Express',        'NE1', 'AC',           'Kathmandu', 'Chitwan',        '07:00', '11:30', '4.5 hrs',    1200, 44, 'Gongabu Bus Park, Kathmandu',  'Bharatpur Bus Park, Chitwan', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rapti Deluxe',            'RD1', 'VOLVO',        'Kathmandu', 'Chitwan',        '06:30', '10:30', '4 hrs',      1800, 40, 'Kalanki, Kathmandu',           'Sauraha, Chitwan',            'AC,WiFi,USB Charging,Blanket,TV Screen'),
            ('Makwanpur Yatayat',       'MY1', 'NON_AC',       'Kathmandu', 'Chitwan',        '06:00', '11:30', '5.5 hrs',    700,  50, 'Gongabu Bus Park, Kathmandu',  'Narayanghat, Chitwan',        'Water Bottle,Emergency Exit'),
            # Chitwan → Kathmandu
            ('Narayani Express',        'NE2', 'AC',           'Chitwan',   'Kathmandu',      '07:00', '11:30', '4.5 hrs',    1200, 44, 'Bharatpur Bus Park, Chitwan',  'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Kathmandu → Butwal / Lumbini
            ('Siddhartha Express',      'SD1', 'AC',           'Kathmandu', 'Butwal',         '07:00', '13:00', '6 hrs',      1300, 44, 'Gongabu Bus Park, Kathmandu',  'Butwal Bus Park',             'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rupandehi Deluxe',        'RU1', 'VOLVO',        'Kathmandu', 'Butwal',         '19:30', '01:30', '6 hrs',      2200, 40, 'Kalanki, Kathmandu',           'Butwal Bus Park',             'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Lumbini Buddha Express',  'LB1', 'AC',           'Kathmandu', 'Lumbini',        '07:00', '14:00', '7 hrs',      1500, 44, 'Gongabu Bus Park, Kathmandu',  'Lumbini Bus Park',            'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Palpa Siddhartha',        'PS1', 'AC',           'Kathmandu', 'Tansen',         '07:00', '14:30', '7.5 hrs',    1400, 44, 'Gongabu Bus Park, Kathmandu',  'Tansen Bus Park, Palpa',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Butwal → Kathmandu
            ('Siddhartha Express',      'SD2', 'AC',           'Butwal',    'Kathmandu',      '07:00', '13:00', '6 hrs',      1300, 44, 'Butwal Bus Park',              'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Kathmandu → Birgunj
            ('Bagmati Express',         'BE1', 'AC',           'Kathmandu', 'Birgunj',        '07:00', '12:30', '5.5 hrs',    1100, 44, 'Gongabu Bus Park, Kathmandu',  'Birgunj Bus Park',            'AC,USB Charging,Water Bottle'),
            ('Parsa Yatayat',           'PA1', 'VOLVO',        'Kathmandu', 'Birgunj',        '06:30', '12:00', '5.5 hrs',    1700, 40, 'Kalanki, Kathmandu',           'Birgunj Bus Park',            'AC,WiFi,USB Charging,Water Bottle,TV Screen'),
            # Kathmandu → Biratnagar / Dharan
            ('Koshi Express',           'KE1', 'AC',           'Kathmandu', 'Biratnagar',     '07:00', '18:00', '11 hrs',     1900, 44, 'Gongabu Bus Park, Kathmandu',  'Biratnagar Bus Park',         'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Koshi Express',           'KE2', 'SLEEPER',      'Kathmandu', 'Biratnagar',     '18:00', '05:00', '11 hrs',     2300, 36, 'Gongabu Bus Park, Kathmandu',  'Biratnagar Bus Park',         'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Sunsari Koshi Sewa',      'SK1', 'AC',           'Kathmandu', 'Dharan',         '07:00', '18:00', '11 hrs',     1900, 44, 'Gongabu Bus Park, Kathmandu',  'Dharan Bus Park',             'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Biratnagar → Kathmandu
            ('Koshi Express',           'KE3', 'AC',           'Biratnagar','Kathmandu',      '07:00', '18:00', '11 hrs',     1900, 44, 'Biratnagar Bus Park',          'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Kathmandu → Janakpur
            ('Mithila Express',         'MI1', 'AC',           'Kathmandu', 'Janakpur',       '07:00', '14:00', '7 hrs',      1200, 44, 'Gongabu Bus Park, Kathmandu',  'Janakpur Bus Park',           'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Janaki Deluxe',           'JD1', 'SEMI_SLEEPER', 'Kathmandu', 'Janakpur',       '19:00', '02:00', '7 hrs',      1500, 38, 'Kalanki, Kathmandu',           'Janakpur Bus Park',           'AC,Blanket,Reclining Seats'),
            # Kathmandu → Nepalgunj
            ('Bheri Express',           'BH1', 'VOLVO',        'Kathmandu', 'Nepalgunj',      '18:00', '07:00', '13 hrs',     2800, 40, 'Gongabu Bus Park, Kathmandu',  'Nepalgunj Bus Park',          'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Karnali Yatayat',         'KR1', 'SLEEPER',      'Kathmandu', 'Nepalgunj',      '17:30', '06:30', '13 hrs',     2400, 36, 'Kalanki, Kathmandu',           'Nepalgunj Bus Park',          'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            # Nepalgunj → Kathmandu
            ('Bheri Express',           'BH2', 'VOLVO',        'Nepalgunj', 'Kathmandu',      '17:00', '06:00', '13 hrs',     2800, 40, 'Nepalgunj Bus Park',           'Gongabu Bus Park, Kathmandu', 'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            # Kathmandu → Dhangadhi
            ('Seti Express',            'ST1', 'SLEEPER',      'Kathmandu', 'Dhangadhi',      '17:00', '07:00', '14 hrs',     2600, 36, 'Gongabu Bus Park, Kathmandu',  'Dhangadhi Bus Park',          'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            # Kathmandu → Gorkha
            ('Gorkha Prithvi Sewa',     'GP1', 'AC',           'Kathmandu', 'Gorkha',         '07:00', '11:00', '4 hrs',      900,  44, 'Gongabu Bus Park, Kathmandu',  'Gorkha Bus Park',             'AC,USB Charging,Water Bottle'),
            # Kathmandu → Baglung
            ('Myagdi Yatayat',          'MY2', 'AC',           'Kathmandu', 'Baglung',        '07:00', '16:00', '9 hrs',      1600, 44, 'Gongabu Bus Park, Kathmandu',  'Baglung Bus Park',            'AC,USB Charging,Water Bottle,Reclining Seats'),
            # Pokhara → Chitwan
            ('Gandaki Narayani Sewa',   'GN1', 'AC',           'Pokhara',   'Chitwan',        '07:00', '11:00', '4 hrs',      900,  44, 'Pokhara Bus Park',             'Bharatpur Bus Park, Chitwan', 'AC,USB Charging,Water Bottle'),
            # Kathmandu → Hetauda
            ('Hetauda Makwanpur Sewa',  'HM1', 'AC',           'Kathmandu', 'Hetauda',        '07:00', '10:30', '3.5 hrs',    800,  44, 'Gongabu Bus Park, Kathmandu',  'Hetauda Bus Park',            'AC,USB Charging,Water Bottle'),
        ]

        today = date.today()
        created = 0
        for idx, (name, prefix, btype, frm, to, dep, arr, dur, price, seats, pickup, dropoff, amenities) in enumerate(routes, 1):
            for day in range(DAYS):
                d = today + timedelta(days=day)
                num = f"{prefix}-{d.strftime('%d%m')}"
                if Bus.objects.filter(bus_number=num).exists():
                    continue
                avail = random.randint(max(1, seats - random.randint(0, seats // 2)), seats)
                Bus.objects.create(
                    bus_number=num, bus_name=name, bus_type=btype,
                    departure_city=frm, destination_city=to,
                    departure_date=d, departure_time=dep, arrival_time=arr,
                    duration=dur, price=price, total_seats=seats, available_seats=avail,
                    amenities=amenities, pickup_point=pickup, dropoff_point=dropoff,
                    is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'    ✓ {created} bus records ({DAYS} days × {len(routes)} routes)'))

    # ------------------------------------------------------------------
    # FLIGHT ROUTES  (~33 unique routes × 3 days = ~99 flight records)
    # ------------------------------------------------------------------
    def create_flights(self):
        self.stdout.write('\n  ✈️  Creating Flight Records...')

        # (flight_number, airline, type, from, to, dep, arr, duration, price, seats, terminal, gate)
        routes = [
            # Domestic — Kathmandu ↔ Pokhara
            ('U4-101', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Pokhara',       '06:00', '06:25', '25 min',          5500,  72,  'Terminal 1', 'Gate 3'),
            ('U4-103', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Pokhara',       '12:30', '12:55', '25 min',          5500,  72,  'Terminal 1', 'Gate 4'),
            ('YT-201', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Pokhara',       '07:30', '07:55', '25 min',          5200,  68,  'Terminal 1', 'Gate 1'),
            ('SH-301', 'Shree Airlines',    'DOMESTIC',      'Kathmandu',  'Pokhara',       '09:00', '09:25', '25 min',          4800,  56,  'Terminal 1', 'Gate 5'),
            ('U4-102', 'Buddha Air',        'DOMESTIC',      'Pokhara',    'Kathmandu',     '07:15', '07:40', '25 min',          5500,  72,  'Terminal 1', 'Gate 1'),
            ('YT-202', 'Yeti Airlines',     'DOMESTIC',      'Pokhara',    'Kathmandu',     '08:45', '09:10', '25 min',          5200,  68,  'Terminal 1', 'Gate 3'),
            # Domestic — Kathmandu ↔ Biratnagar
            ('U4-501', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Biratnagar',    '07:00', '07:40', '40 min',          7500,  72,  'Terminal 1', 'Gate 7'),
            ('YT-511', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Biratnagar',    '10:30', '11:10', '40 min',          7200,  68,  'Terminal 1', 'Gate 8'),
            ('U4-502', 'Buddha Air',        'DOMESTIC',      'Biratnagar', 'Kathmandu',     '08:30', '09:10', '40 min',          7500,  72,  'Terminal 1', 'Gate 1'),
            # Domestic — Kathmandu ↔ Nepalgunj
            ('U4-601', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Nepalgunj',     '08:00', '09:10', '1 hr 10 min',     10500, 72,  'Terminal 1', 'Gate 9'),
            ('YT-611', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Nepalgunj',     '10:30', '11:40', '1 hr 10 min',     10200, 68,  'Terminal 1', 'Gate 9'),
            ('U4-602', 'Buddha Air',        'DOMESTIC',      'Nepalgunj',  'Kathmandu',     '10:00', '11:10', '1 hr 10 min',     10500, 72,  'Terminal 1', 'Gate 2'),
            # Domestic — Kathmandu ↔ Janakpur
            ('U4-701', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Janakpur',      '07:30', '08:05', '35 min',          6500,  72,  'Terminal 1', 'Gate 11'),
            ('YT-711', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Janakpur',      '09:00', '09:35', '35 min',          6200,  68,  'Terminal 1', 'Gate 11'),
            ('U4-702', 'Buddha Air',        'DOMESTIC',      'Janakpur',   'Kathmandu',     '09:30', '10:05', '35 min',          6500,  72,  'Terminal 1', 'Gate 2'),
            # Domestic — Kathmandu ↔ Dhangadhi
            ('U4-801', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Dhangadhi',     '09:00', '10:25', '1 hr 25 min',     12000, 72,  'Terminal 1', 'Gate 12'),
            ('YT-811', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Dhangadhi',     '11:00', '12:25', '1 hr 25 min',     11500, 68,  'Terminal 1', 'Gate 12'),
            # Domestic — Kathmandu → Lukla
            ('U4-901', 'Buddha Air',        'DOMESTIC',      'Kathmandu',  'Lukla',         '06:00', '06:30', '30 min',          18000, 20,  'Terminal 1', 'Gate 13'),
            ('YT-911', 'Yeti Airlines',     'DOMESTIC',      'Kathmandu',  'Lukla',         '06:30', '07:00', '30 min',          17500, 20,  'Terminal 1', 'Gate 13'),
            # International — Kathmandu → Delhi
            ('AI-901', 'Air India',         'INTERNATIONAL', 'Kathmandu',  'Delhi',         '08:00', '10:30', '2 hrs 30 min',    18000, 156, 'Terminal 2', 'Gate A1'),
            ('6E-911', 'IndiGo',            'INTERNATIONAL', 'Kathmandu',  'Delhi',         '15:30', '18:00', '2 hrs 30 min',    16000, 180, 'Terminal 2', 'Gate A2'),
            ('RA-921', 'Nepal Airlines',    'INTERNATIONAL', 'Kathmandu',  'Delhi',         '10:00', '12:30', '2 hrs 30 min',    17500, 140, 'Terminal 2', 'Gate A3'),
            # International — Kathmandu → Dubai
            ('EK-A01', 'Emirates',          'INTERNATIONAL', 'Kathmandu',  'Dubai',         '02:15', '05:45', '5 hrs 30 min',    55000, 300, 'Terminal 2', 'Gate B1'),
            ('FZ-A11', 'Flydubai',          'INTERNATIONAL', 'Kathmandu',  'Dubai',         '23:55', '03:25', '5 hrs 30 min',    42000, 189, 'Terminal 2', 'Gate B2'),
            # International — Kathmandu → Doha
            ('QR-B01', 'Qatar Airways',     'INTERNATIONAL', 'Kathmandu',  'Doha',          '03:00', '07:00', '5 hrs',           60000, 300, 'Terminal 2', 'Gate C1'),
            # International — Kathmandu → Kuala Lumpur
            ('MH-C01', 'Malaysia Airlines', 'INTERNATIONAL', 'Kathmandu',  'Kuala Lumpur',  '00:30', '08:30', '5 hrs',           52000, 300, 'Terminal 2', 'Gate D1'),
            ('AK-C11', 'AirAsia',           'INTERNATIONAL', 'Kathmandu',  'Kuala Lumpur',  '02:00', '10:00', '5 hrs',           38000, 180, 'Terminal 2', 'Gate D2'),
            # International — Kathmandu → Bangkok
            ('TG-D01', 'Thai Airways',      'INTERNATIONAL', 'Kathmandu',  'Bangkok',       '01:00', '06:30', '3 hrs 30 min',    45000, 300, 'Terminal 2', 'Gate E1'),
            ('FD-D11', 'Thai AirAsia',      'INTERNATIONAL', 'Kathmandu',  'Bangkok',       '23:30', '05:00', '3 hrs 30 min',    32000, 180, 'Terminal 2', 'Gate E2'),
            # International — Kathmandu → Singapore
            ('SQ-E01', 'Singapore Airlines','INTERNATIONAL', 'Kathmandu',  'Singapore',     '00:45', '07:45', '4 hrs',           70000, 280, 'Terminal 2', 'Gate F1'),
            ('TR-E11', 'Scoot',             'INTERNATIONAL', 'Kathmandu',  'Singapore',     '02:30', '09:30', '4 hrs',           40000, 180, 'Terminal 2', 'Gate F2'),
            # International — Kathmandu → Hong Kong
            ('CX-F01', 'Cathay Pacific',    'INTERNATIONAL', 'Kathmandu',  'Hong Kong',     '01:15', '08:15', '5 hrs',           75000, 280, 'Terminal 2', 'Gate G1'),
        ]

        today = date.today()
        created = 0
        for (num, airline, ftype, frm, to, dep, arr, dur, price, seats, terminal, gate) in routes:
            for day in range(DAYS):
                d = today + timedelta(days=day)
                flight_num = f"{num}-{d.strftime('%d%m')}"
                if Flight.objects.filter(flight_number=flight_num).exists():
                    continue
                avail = random.randint(max(1, seats - random.randint(0, seats // 3)), seats)
                Flight.objects.create(
                    flight_number=flight_num, airline=airline, flight_type=ftype,
                    departure_city=frm, destination_city=to,
                    departure_date=d, departure_time=dep, arrival_time=arr,
                    duration=dur, price=price, total_seats=seats, available_seats=avail,
                    terminal=terminal, gate=gate, is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'    ✓ {created} flight records ({DAYS} days × {len(routes)} routes)'))
