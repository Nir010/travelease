"""
TravelEase - Realistic Nepal Bus & Flight Data
==============================================
Buses are named after their origin/destination region — the authentic Nepal pattern.
e.g., Kathmandu → Waling  →  "Syangja Gandaki Yatayat"
      Kathmandu → Pokhara →  "Gandaki Express / Annapurna Deluxe"
      Kathmandu → Chitwan →  "Narayani Express"

Usage:
  python manage.py populate_real_data
  python manage.py populate_real_data --clear
"""

from django.core.management.base import BaseCommand
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

        self.stdout.write(self.style.WARNING('\n🚌✈️  TravelEase — Realistic Nepal Data\n' + '=' * 50))
        self.create_buses()
        self.create_flights()
        self.stdout.write(self.style.SUCCESS('\n✅ Done! Nepal routes loaded.\n'))

    # ------------------------------------------------------------------
    # BUS DATA — named after their regional origin/destination
    # ------------------------------------------------------------------
    def create_buses(self):
        self.stdout.write('\n  🚌 Creating Bus Records...')

        # fmt: (bus_name, number_prefix, bus_type, from, to, dep_time, arr_time, duration, price_npr, seats, pickup, dropoff, amenities)
        bus_routes = [

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → POKHARA  (Gandaki Province)
            # ═══════════════════════════════════════════════════════
            ('Gandaki Express',        'GE', 'AC',          'Kathmandu', 'Pokhara',    '06:30', '13:30', '7 hrs',    1800, 42, 'Gongabu Bus Park, Kathmandu', 'Pokhara Bus Park',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Annapurna Deluxe',       'AN', 'VOLVO',       'Kathmandu', 'Pokhara',    '07:00', '13:30', '6.5 hrs',  2400, 40, 'Kalanki, Kathmandu',          'Pokhara Lakeside',      'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Prithvi Highway Express','PH', 'AC',          'Kathmandu', 'Pokhara',    '08:30', '15:30', '7 hrs',    1600, 44, 'Gongabu Bus Park, Kathmandu', 'Pokhara Bus Park',      'AC,USB Charging,Water Bottle'),
            ('Machhapuchhre Travels',  'MC', 'SEMI_SLEEPER','Kathmandu', 'Pokhara',    '20:00', '03:00', '7 hrs',    1700, 38, 'Gongabu Bus Park, Kathmandu', 'Pokhara Bus Park',      'AC,Reclining Seats,Blanket,USB Charging'),
            ('Mustang Deluxe',         'MU', 'VOLVO',       'Kathmandu', 'Pokhara',    '19:30', '02:00', '6.5 hrs',  2500, 40, 'Kalanki, Kathmandu',          'Pokhara Lakeside',      'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Pokhara Tourist Bus',    'PT', 'AC',          'Kathmandu', 'Pokhara',    '07:30', '14:00', '6.5 hrs',  2200, 40, 'Thamel, Kathmandu',           'Pokhara Lakeside',      'AC,WiFi,USB Charging,Water Bottle,Snacks'),
            ('Kaligandaki Yatayat',    'KG', 'NON_AC',      'Kathmandu', 'Pokhara',    '06:00', '13:30', '7.5 hrs',  900,  50, 'Gongabu Bus Park, Kathmandu', 'Pokhara Bus Park',      'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → WALING / SYANGJA
            # ═══════════════════════════════════════════════════════
            ('Syangja Gandaki Yatayat','SG', 'AC',          'Kathmandu', 'Waling',     '07:00', '15:00', '8 hrs',    1500, 44, 'Gongabu Bus Park, Kathmandu', 'Waling Bus Park, Syangja',    'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Syangja Gandaki Yatayat','SG', 'AC',          'Kathmandu', 'Waling',     '19:00', '03:00', '8 hrs',    1600, 44, 'Kalanki, Kathmandu',          'Waling Bus Park, Syangja',    'AC,USB Charging,Blanket,Reclining Seats'),
            ('Kaligandaki Syangja',    'KS', 'NON_AC',      'Kathmandu', 'Waling',     '06:30', '15:00', '8.5 hrs',  1000, 48, 'Gongabu Bus Park, Kathmandu', 'Waling Bus Park, Syangja',    'Water Bottle,Emergency Exit'),
            ('Syangja Express',        'SE', 'AC',          'Kathmandu', 'Syangja',    '07:00', '15:30', '8.5 hrs',  1500, 44, 'Gongabu Bus Park, Kathmandu', 'Syangja Bus Park',            'AC,USB Charging,Water Bottle'),
            ('Gandaki Syangja Sewa',   'GS', 'SEMI_SLEEPER','Kathmandu', 'Waling',     '20:30', '04:30', '8 hrs',    1700, 38, 'Kalanki, Kathmandu',          'Waling Bus Park, Syangja',    'AC,Blanket,Reclining Seats,USB Charging'),

            # ═══════════════════════════════════════════════════════
            # POKHARA → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Gandaki Express',        'GE', 'AC',          'Pokhara', 'Kathmandu',   '07:00', '14:00', '7 hrs',    1800, 42, 'Pokhara Bus Park',       'Gongabu Bus Park, Kathmandu',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Annapurna Deluxe',       'AN', 'VOLVO',       'Pokhara', 'Kathmandu',   '07:00', '13:30', '6.5 hrs',  2400, 40, 'Pokhara Lakeside',       'Kalanki, Kathmandu',            'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Machhapuchhre Travels',  'MC', 'AC',          'Pokhara', 'Kathmandu',   '08:00', '15:00', '7 hrs',    1700, 42, 'Pokhara Bus Park',       'Gongabu Bus Park, Kathmandu',  'AC,USB Charging,Water Bottle'),
            ('Kaligandaki Yatayat',    'KG', 'NON_AC',      'Pokhara', 'Kathmandu',   '06:00', '13:30', '7.5 hrs',  900,  50, 'Pokhara Bus Park',       'Gongabu Bus Park, Kathmandu',  'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # WALING / SYANGJA → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Syangja Gandaki Yatayat','SG', 'AC',          'Waling', 'Kathmandu',   '06:00', '14:00', '8 hrs',    1500, 44, 'Waling Bus Park, Syangja', 'Gongabu Bus Park, Kathmandu',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Syangja Express',        'SE', 'AC',          'Syangja', 'Kathmandu',   '06:30', '15:00', '8.5 hrs',  1500, 44, 'Syangja Bus Park',         'Gongabu Bus Park, Kathmandu',  'AC,USB Charging,Water Bottle'),
            ('Kaligandaki Syangja',    'KS', 'NON_AC',      'Waling', 'Kathmandu',   '06:00', '14:30', '8.5 hrs',  1000, 48, 'Waling Bus Park, Syangja', 'Gongabu Bus Park, Kathmandu',  'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → CHITWAN  (Narayani / Rapti region)
            # ═══════════════════════════════════════════════════════
            ('Narayani Express',       'NE', 'AC',          'Kathmandu', 'Chitwan',    '07:00', '11:30', '4.5 hrs',  1200, 44, 'Gongabu Bus Park, Kathmandu', 'Bharatpur Bus Park, Chitwan',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rapti Deluxe',           'RD', 'VOLVO',       'Kathmandu', 'Chitwan',    '06:30', '10:30', '4 hrs',    1800, 40, 'Kalanki, Kathmandu',          'Sauraha, Chitwan',             'AC,WiFi,USB Charging,Blanket,TV Screen'),
            ('Chitwan Sauraha Bus',    'CS', 'AC',          'Kathmandu', 'Chitwan',    '07:30', '12:00', '4.5 hrs',  1300, 42, 'Thamel, Kathmandu',           'Sauraha, Chitwan',             'AC,USB Charging,Water Bottle,Snacks'),
            ('Makwanpur Yatayat',      'MY', 'NON_AC',      'Kathmandu', 'Chitwan',    '06:00', '11:30', '5.5 hrs',  700,  50, 'Gongabu Bus Park, Kathmandu', 'Narayanghat, Chitwan',         'Water Bottle,Emergency Exit'),
            ('Chitwan Express',        'CE', 'SEMI_SLEEPER','Kathmandu', 'Chitwan',    '20:30', '01:00', '4.5 hrs',  1400, 38, 'Kalanki, Kathmandu',          'Bharatpur Bus Park, Chitwan',  'AC,Reclining Seats,Blanket'),

            # ═══════════════════════════════════════════════════════
            # CHITWAN → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Narayani Express',       'NE', 'AC',          'Chitwan', 'Kathmandu',   '07:00', '11:30', '4.5 hrs',  1200, 44, 'Bharatpur Bus Park, Chitwan', 'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rapti Deluxe',           'RD', 'VOLVO',       'Chitwan', 'Kathmandu',   '07:00', '11:00', '4 hrs',    1800, 40, 'Sauraha, Chitwan',            'Kalanki, Kathmandu',           'AC,WiFi,USB Charging,Blanket,TV Screen'),
            ('Makwanpur Yatayat',      'MY', 'NON_AC',      'Chitwan', 'Kathmandu',   '06:00', '11:30', '5.5 hrs',  700,  50, 'Narayanghat, Chitwan',        'Gongabu Bus Park, Kathmandu', 'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → BUTWAL / LUMBINI  (Siddhartha region)
            # ═══════════════════════════════════════════════════════
            ('Siddhartha Express',     'SD', 'AC',          'Kathmandu', 'Butwal',     '07:00', '13:00', '6 hrs',    1300, 44, 'Gongabu Bus Park, Kathmandu', 'Butwal Bus Park',       'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Lumbini Yatayat',        'LY', 'AC',          'Kathmandu', 'Butwal',     '07:30', '13:30', '6 hrs',    1300, 44, 'Gongabu Bus Park, Kathmandu', 'Butwal Bus Park',       'AC,USB Charging,Water Bottle'),
            ('Rupandehi Deluxe',       'RU', 'VOLVO',       'Kathmandu', 'Butwal',     '19:30', '01:30', '6 hrs',    2200, 40, 'Kalanki, Kathmandu',          'Butwal Bus Park',       'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Lumbini Buddha Express', 'LB', 'AC',          'Kathmandu', 'Lumbini',    '07:00', '14:00', '7 hrs',    1500, 44, 'Gongabu Bus Park, Kathmandu', 'Lumbini Bus Park',      'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Kapilvastu Yatayat',     'KV', 'NON_AC',      'Kathmandu', 'Lumbini',    '06:30', '14:00', '7.5 hrs',  900,  50, 'Gongabu Bus Park, Kathmandu', 'Lumbini Bus Park',      'Water Bottle,Emergency Exit'),
            ('Palpa Siddhartha',       'PS', 'AC',          'Kathmandu', 'Tansen',     '07:00', '14:30', '7.5 hrs',  1400, 44, 'Gongabu Bus Park, Kathmandu', 'Tansen Bus Park, Palpa','AC,USB Charging,Water Bottle,Reclining Seats'),

            # ═══════════════════════════════════════════════════════
            # BUTWAL → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Siddhartha Express',     'SD', 'AC',          'Butwal', 'Kathmandu',   '07:00', '13:00', '6 hrs',    1300, 44, 'Butwal Bus Park', 'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rupandehi Deluxe',       'RU', 'VOLVO',       'Butwal', 'Kathmandu',   '19:30', '01:30', '6 hrs',    2200, 40, 'Butwal Bus Park', 'Kalanki, Kathmandu',          'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Lumbini Yatayat',        'LY', 'NON_AC',      'Butwal', 'Kathmandu',   '06:00', '13:00', '7 hrs',    800,  50, 'Butwal Bus Park', 'Gongabu Bus Park, Kathmandu', 'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → BIRGUNJ  (Bagmati / Parsa region)
            # ═══════════════════════════════════════════════════════
            ('Bagmati Express',        'BE', 'AC',          'Kathmandu', 'Birgunj',    '07:00', '12:30', '5.5 hrs',  1100, 44, 'Gongabu Bus Park, Kathmandu', 'Birgunj Bus Park',  'AC,USB Charging,Water Bottle'),
            ('Parsa Yatayat',          'PA', 'VOLVO',       'Kathmandu', 'Birgunj',    '06:30', '12:00', '5.5 hrs',  1700, 40, 'Kalanki, Kathmandu',          'Birgunj Bus Park',  'AC,WiFi,USB Charging,Water Bottle,TV Screen'),
            ('Narayani Border Express','NB', 'NON_AC',      'Kathmandu', 'Birgunj',    '06:00', '12:30', '6.5 hrs',  700,  50, 'Gongabu Bus Park, Kathmandu', 'Birgunj Bus Park',  'Water Bottle,Emergency Exit'),
            ('Hetauda Makwanpur Sewa', 'HM', 'AC',          'Kathmandu', 'Hetauda',    '07:00', '10:30', '3.5 hrs',  800,  44, 'Gongabu Bus Park, Kathmandu', 'Hetauda Bus Park',  'AC,USB Charging,Water Bottle'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → BIRATNAGAR / DHARAN  (Koshi Province)
            # ═══════════════════════════════════════════════════════
            ('Koshi Express',          'KE', 'AC',          'Kathmandu', 'Biratnagar', '07:00', '18:00', '11 hrs',   1900, 44, 'Gongabu Bus Park, Kathmandu', 'Biratnagar Bus Park', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Koshi Express',          'KE', 'SLEEPER',     'Kathmandu', 'Biratnagar', '18:00', '05:00', '11 hrs',   2300, 36, 'Gongabu Bus Park, Kathmandu', 'Biratnagar Bus Park', 'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Morang Yatayat',         'MO', 'SEMI_SLEEPER','Kathmandu', 'Biratnagar', '17:30', '04:30', '11 hrs',   2000, 38, 'Kalanki, Kathmandu',          'Biratnagar Bus Park', 'AC,Blanket,Reclining Seats'),
            ('Sunsari Koshi Sewa',     'SK', 'AC',          'Kathmandu', 'Dharan',     '07:00', '18:00', '11 hrs',   1900, 44, 'Gongabu Bus Park, Kathmandu', 'Dharan Bus Park',     'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Sunsari Koshi Sewa',     'SK', 'SLEEPER',     'Kathmandu', 'Dharan',     '17:30', '04:30', '11 hrs',   2200, 36, 'Gongabu Bus Park, Kathmandu', 'Dharan Bus Park',     'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Mechi Express',          'MX', 'AC',          'Kathmandu', 'Bhadrapur',  '17:00', '05:00', '12 hrs',   2100, 44, 'Gongabu Bus Park, Kathmandu', 'Bhadrapur Bus Park',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Ilam Mechi Yatayat',     'IL', 'SEMI_SLEEPER','Kathmandu', 'Ilam',       '17:00', '06:00', '13 hrs',   2200, 38, 'Gongabu Bus Park, Kathmandu', 'Ilam Bus Park',       'AC,Blanket,Reclining Seats'),

            # ═══════════════════════════════════════════════════════
            # BIRATNAGAR / DHARAN → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Koshi Express',          'KE', 'AC',          'Biratnagar', 'Kathmandu', '07:00', '18:00', '11 hrs',   1900, 44, 'Biratnagar Bus Park', 'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Koshi Express',          'KE', 'SLEEPER',     'Biratnagar', 'Kathmandu', '17:00', '04:00', '11 hrs',   2300, 36, 'Biratnagar Bus Park', 'Gongabu Bus Park, Kathmandu', 'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Sunsari Koshi Sewa',     'SK', 'AC',          'Dharan',     'Kathmandu', '07:00', '18:00', '11 hrs',   1900, 44, 'Dharan Bus Park',     'Gongabu Bus Park, Kathmandu', 'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Morang Yatayat',         'MO', 'NON_AC',      'Biratnagar', 'Kathmandu', '06:30', '18:00', '11.5 hrs', 1100, 50, 'Biratnagar Bus Park', 'Gongabu Bus Park, Kathmandu', 'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → JANAKPUR  (Madhesh / Mithila region)
            # ═══════════════════════════════════════════════════════
            ('Mithila Express',        'MI', 'AC',          'Kathmandu', 'Janakpur',   '07:00', '14:00', '7 hrs',    1200, 44, 'Gongabu Bus Park, Kathmandu', 'Janakpur Bus Park',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Janaki Deluxe',          'JD', 'SEMI_SLEEPER','Kathmandu', 'Janakpur',   '19:00', '02:00', '7 hrs',    1500, 38, 'Kalanki, Kathmandu',          'Janakpur Bus Park',  'AC,Blanket,Reclining Seats'),
            ('Dhanusha Yatayat',       'DH', 'NON_AC',      'Kathmandu', 'Janakpur',   '06:30', '14:30', '8 hrs',    800,  50, 'Gongabu Bus Park, Kathmandu', 'Janakpur Bus Park',  'Water Bottle,Emergency Exit'),
            ('Sarlahi Sewa',           'SR', 'AC',          'Kathmandu', 'Malangwa',   '07:00', '13:00', '6 hrs',    1100, 44, 'Gongabu Bus Park, Kathmandu', 'Malangwa Bus Park',  'AC,USB Charging,Water Bottle'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → NEPALGUNJ / FAR WEST  (Bheri / Karnali)
            # ═══════════════════════════════════════════════════════
            ('Bheri Express',          'BH', 'VOLVO',       'Kathmandu', 'Nepalgunj',  '18:00', '07:00', '13 hrs',   2800, 40, 'Gongabu Bus Park, Kathmandu', 'Nepalgunj Bus Park',  'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Karnali Yatayat',        'KR', 'SLEEPER',     'Kathmandu', 'Nepalgunj',  '17:30', '06:30', '13 hrs',   2400, 36, 'Kalanki, Kathmandu',          'Nepalgunj Bus Park',  'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Banke Sewa',             'BN', 'AC',          'Kathmandu', 'Nepalgunj',  '18:30', '07:30', '13 hrs',   2000, 44, 'Gongabu Bus Park, Kathmandu', 'Nepalgunj Bus Park',  'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Seti Express',           'ST', 'SLEEPER',     'Kathmandu', 'Dhangadhi',  '17:00', '07:00', '14 hrs',   2600, 36, 'Gongabu Bus Park, Kathmandu', 'Dhangadhi Bus Park',  'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),
            ('Mahakali Yatayat',       'MK', 'AC',          'Kathmandu', 'Mahendranagar','17:00','08:30','15.5 hrs', 2900, 44, 'Gongabu Bus Park, Kathmandu', 'Mahendranagar Bus Park','AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Kailali Karnali Sewa',   'KK', 'NON_AC',      'Kathmandu', 'Dhangadhi',  '17:30', '08:00', '14.5 hrs', 1500, 50, 'Gongabu Bus Park, Kathmandu', 'Dhangadhi Bus Park',  'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # NEPALGUNJ → KATHMANDU
            # ═══════════════════════════════════════════════════════
            ('Bheri Express',          'BH', 'VOLVO',       'Nepalgunj', 'Kathmandu',  '17:00', '06:00', '13 hrs',   2800, 40, 'Nepalgunj Bus Park', 'Gongabu Bus Park, Kathmandu', 'AC,WiFi,USB Charging,Blanket,TV Screen,Reclining Seats'),
            ('Karnali Yatayat',        'KR', 'SLEEPER',     'Nepalgunj', 'Kathmandu',  '17:30', '06:30', '13 hrs',   2400, 36, 'Nepalgunj Bus Park', 'Kalanki, Kathmandu',           'AC,Blanket,USB Charging,Reclining Seats,Reading Light'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → GORKHA / BESISAHAR  (Gandaki hills)
            # ═══════════════════════════════════════════════════════
            ('Gorkha Prithvi Sewa',    'GP', 'AC',          'Kathmandu', 'Gorkha',     '07:00', '11:00', '4 hrs',    900,  44, 'Gongabu Bus Park, Kathmandu', 'Gorkha Bus Park',     'AC,USB Charging,Water Bottle'),
            ('Gorkha Prithvi Sewa',    'GP', 'NON_AC',      'Kathmandu', 'Gorkha',     '06:30', '11:00', '4.5 hrs',  600,  50, 'Gongabu Bus Park, Kathmandu', 'Gorkha Bus Park',     'Water Bottle,Emergency Exit'),
            ('Manaslu Besisahar Sewa', 'MB', 'AC',          'Kathmandu', 'Besisahar',  '07:00', '12:30', '5.5 hrs',  1000, 44, 'Gongabu Bus Park, Kathmandu', 'Besisahar Bus Park',  'AC,USB Charging,Water Bottle'),
            ('Lamjung Yatayat',        'LA', 'NON_AC',      'Kathmandu', 'Besisahar',  '06:30', '12:30', '6 hrs',    700,  50, 'Gongabu Bus Park, Kathmandu', 'Besisahar Bus Park',  'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # POKHARA → CHITWAN / BUTWAL
            # ═══════════════════════════════════════════════════════
            ('Gandaki Narayani Sewa',  'GN', 'AC',          'Pokhara', 'Chitwan',     '07:00', '11:00', '4 hrs',    900,  44, 'Pokhara Bus Park',   'Bharatpur Bus Park, Chitwan',  'AC,USB Charging,Water Bottle'),
            ('Prithvi Narayani Sewa',  'PN', 'NON_AC',      'Pokhara', 'Chitwan',     '06:30', '11:30', '5 hrs',    600,  50, 'Pokhara Bus Park',   'Narayanghat, Chitwan',         'Water Bottle,Emergency Exit'),
            ('Siddhartha Gandaki',     'SG', 'AC',          'Pokhara', 'Butwal',      '07:30', '12:00', '4.5 hrs',  950,  44, 'Pokhara Bus Park',   'Butwal Bus Park',               'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Rupandehi Gandaki Sewa', 'RG', 'NON_AC',      'Pokhara', 'Butwal',      '07:00', '12:00', '5 hrs',    650,  50, 'Pokhara Bus Park',   'Butwal Bus Park',               'Water Bottle,Emergency Exit'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → SINDHULI / RAMECHHAP  (Tamakoshi region)
            # ═══════════════════════════════════════════════════════
            ('Tamakoshi Express',      'TE', 'AC',          'Kathmandu', 'Sindhuli',   '07:00', '12:30', '5.5 hrs',  1000, 44, 'Koteshwor, Kathmandu', 'Sindhuli Bus Park',    'AC,USB Charging,Water Bottle'),
            ('Sindhuli Yatayat',       'SI', 'NON_AC',      'Kathmandu', 'Sindhuli',   '06:30', '13:00', '6.5 hrs',  650,  50, 'Koteshwor, Kathmandu', 'Sindhuli Bus Park',    'Water Bottle,Emergency Exit'),
            ('Ramechhap Tamakoshi',    'RT', 'AC',          'Kathmandu', 'Ramechhap',  '07:00', '13:00', '6 hrs',    1000, 44, 'Koteshwor, Kathmandu', 'Ramechhap Bus Park',   'AC,USB Charging,Water Bottle'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → DHULIKHEL / BANEPA  (Kavrepalanchok)
            # ═══════════════════════════════════════════════════════
            ('Kavre Yatayat',          'KV', 'NON_AC',      'Kathmandu', 'Dhulikhel',  '06:00', '07:30', '1.5 hrs',  250,  44, 'Ratnapark, Kathmandu', 'Dhulikhel Bus Park',   'Water Bottle'),
            ('Banepa Sewa',            'BS', 'NON_AC',      'Kathmandu', 'Banepa',     '06:00', '07:15', '1.25 hrs', 200,  44, 'Ratnapark, Kathmandu', 'Banepa Bus Park',      'Water Bottle'),

            # ═══════════════════════════════════════════════════════
            # KATHMANDU → POKHARA → BAGLUNG / BENI  (Myagdi region)
            # ═══════════════════════════════════════════════════════
            ('Myagdi Yatayat',         'MY', 'AC',          'Kathmandu', 'Baglung',    '07:00', '16:00', '9 hrs',    1600, 44, 'Gongabu Bus Park, Kathmandu', 'Baglung Bus Park',    'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Kali Gandaki Myagdi',    'KM', 'NON_AC',      'Kathmandu', 'Baglung',    '06:30', '16:00', '9.5 hrs',  1000, 50, 'Gongabu Bus Park, Kathmandu', 'Baglung Bus Park',    'Water Bottle,Emergency Exit'),
            ('Annapurna Beni Sewa',    'AB', 'AC',          'Kathmandu', 'Beni',       '07:00', '17:00', '10 hrs',   1700, 44, 'Gongabu Bus Park, Kathmandu', 'Beni Bus Park',       'AC,USB Charging,Water Bottle,Reclining Seats'),
            ('Mustang Tukuche Sewa',   'MS', 'SEMI_SLEEPER','Kathmandu', 'Jomsom',     '06:00', '18:00', '12 hrs',   2200, 38, 'Gongabu Bus Park, Kathmandu', 'Jomsom Bus Park',     'AC,Blanket,Reclining Seats,USB Charging'),
        ]

        today = date.today()
        created = 0
        # unique suffix per route+operator to avoid duplicates
        route_counter = {}

        for (bus_name, prefix, btype, from_city, to_city,
             dep_t, arr_t, duration, price, seats,
             pickup, dropoff, amenities) in bus_routes:

            route_key = f"{prefix}-{from_city[:3].upper()}{to_city[:3].upper()}"
            route_counter[route_key] = route_counter.get(route_key, 0) + 1
            seq = route_counter[route_key]

            for day_offset in range(7):
                travel_date = today + timedelta(days=day_offset)
                bus_number = f"{route_key}{seq:02d}-{travel_date.strftime('%d%m')}"

                if Bus.objects.filter(bus_number=bus_number).exists():
                    continue

                avail = random.randint(max(1, seats - random.randint(0, seats // 2)), seats)
                Bus.objects.create(
                    bus_number=bus_number,
                    bus_name=bus_name,
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

        flight_data = [
            # ── DOMESTIC — KATHMANDU ↔ POKHARA ──
            ('U4-101', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '06:00', '06:25', '25 min',       5500,  72,  'Terminal 1', 'Gate 3'),
            ('U4-103', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '09:15', '09:40', '25 min',       5500,  72,  'Terminal 1', 'Gate 3'),
            ('U4-105', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Pokhara',    '12:30', '12:55', '25 min',       5500,  72,  'Terminal 1', 'Gate 4'),
            ('YT-201', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Pokhara',    '07:30', '07:55', '25 min',       5200,  68,  'Terminal 1', 'Gate 1'),
            ('YT-203', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Pokhara',    '11:00', '11:25', '25 min',       5200,  68,  'Terminal 1', 'Gate 2'),
            ('SH-301', 'Shree Airlines','DOMESTIC', 'Kathmandu', 'Pokhara',    '08:00', '08:25', '25 min',       4800,  56,  'Terminal 1', 'Gate 5'),
            ('SA-401', 'Saurya Airlines','DOMESTIC','Kathmandu', 'Pokhara',    '09:00', '09:25', '25 min',       4500,  50,  'Terminal 1', 'Gate 6'),
            ('U4-102', 'Buddha Air',    'DOMESTIC', 'Pokhara',   'Kathmandu',  '07:15', '07:40', '25 min',       5500,  72,  'Terminal 1', 'Gate 1'),
            ('YT-202', 'Yeti Airlines', 'DOMESTIC', 'Pokhara',   'Kathmandu',  '08:45', '09:10', '25 min',       5200,  68,  'Terminal 1', 'Gate 3'),
            ('SH-302', 'Shree Airlines','DOMESTIC', 'Pokhara',   'Kathmandu',  '09:15', '09:40', '25 min',       4800,  56,  'Terminal 1', 'Gate 4'),

            # ── DOMESTIC — KATHMANDU ↔ BIRATNAGAR ──
            ('U4-501', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Biratnagar', '07:00', '07:40', '40 min',       7500,  72,  'Terminal 1', 'Gate 7'),
            ('U4-503', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Biratnagar', '10:30', '11:10', '40 min',       7500,  72,  'Terminal 1', 'Gate 7'),
            ('YT-511', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Biratnagar', '08:00', '08:40', '40 min',       7200,  68,  'Terminal 1', 'Gate 8'),
            ('U4-502', 'Buddha Air',    'DOMESTIC', 'Biratnagar','Kathmandu',  '08:30', '09:10', '40 min',       7500,  72,  'Terminal 1', 'Gate 1'),
            ('YT-512', 'Yeti Airlines', 'DOMESTIC', 'Biratnagar','Kathmandu',  '09:30', '10:10', '40 min',       7200,  68,  'Terminal 1', 'Gate 2'),

            # ── DOMESTIC — KATHMANDU ↔ NEPALGUNJ ──
            ('U4-601', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Nepalgunj',  '08:00', '09:10', '1 hr 10 min',  10500, 72,  'Terminal 1', 'Gate 9'),
            ('YT-611', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Nepalgunj',  '09:30', '10:40', '1 hr 10 min',  10200, 68,  'Terminal 1', 'Gate 9'),
            ('U4-602', 'Buddha Air',    'DOMESTIC', 'Nepalgunj', 'Kathmandu',  '10:00', '11:10', '1 hr 10 min',  10500, 72,  'Terminal 1', 'Gate 1'),

            # ── DOMESTIC — KATHMANDU ↔ JANAKPUR ──
            ('U4-701', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Janakpur',   '07:30', '08:05', '35 min',       6500,  72,  'Terminal 1', 'Gate 11'),
            ('YT-711', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Janakpur',   '09:00', '09:35', '35 min',       6200,  68,  'Terminal 1', 'Gate 11'),
            ('U4-702', 'Buddha Air',    'DOMESTIC', 'Janakpur',  'Kathmandu',  '09:00', '09:35', '35 min',       6500,  72,  'Terminal 1', 'Gate 1'),

            # ── DOMESTIC — KATHMANDU ↔ DHANGADHI ──
            ('U4-801', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Dhangadhi',  '09:00', '10:25', '1 hr 25 min',  12000, 72,  'Terminal 1', 'Gate 12'),
            ('YT-811', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Dhangadhi',  '10:30', '11:55', '1 hr 25 min',  11500, 68,  'Terminal 1', 'Gate 12'),
            ('U4-802', 'Buddha Air',    'DOMESTIC', 'Dhangadhi', 'Kathmandu',  '11:30', '12:55', '1 hr 25 min',  12000, 72,  'Terminal 1', 'Gate 1'),

            # ── DOMESTIC — KATHMANDU ↔ TUMLINGTAR / LUKLA ──
            ('U4-901', 'Buddha Air',    'DOMESTIC', 'Kathmandu', 'Lukla',      '06:00', '06:30', '30 min',       18000, 20,  'Terminal 1', 'Gate 13'),
            ('YT-911', 'Yeti Airlines', 'DOMESTIC', 'Kathmandu', 'Lukla',      '06:30', '07:00', '30 min',       17500, 20,  'Terminal 1', 'Gate 13'),

            # ── INTERNATIONAL — KATHMANDU → DELHI ──
            ('AI-901', 'Air India',         'INTERNATIONAL', 'Kathmandu', 'Delhi',        '08:00', '10:30', '2 hrs 30 min',  18000, 156, 'Terminal 2', 'Gate A1'),
            ('6E-911', 'IndiGo',            'INTERNATIONAL', 'Kathmandu', 'Delhi',        '09:30', '12:00', '2 hrs 30 min',  16000, 180, 'Terminal 2', 'Gate A2'),
            ('RA-921', 'Nepal Airlines',    'INTERNATIONAL', 'Kathmandu', 'Delhi',        '10:00', '12:30', '2 hrs 30 min',  17500, 140, 'Terminal 2', 'Gate A3'),
            ('SG-931', 'SpiceJet',          'INTERNATIONAL', 'Kathmandu', 'Delhi',        '15:30', '18:00', '2 hrs 30 min',  14500, 180, 'Terminal 2', 'Gate A4'),

            # ── INTERNATIONAL — KATHMANDU → DUBAI ──
            ('EK-A01', 'Emirates',          'INTERNATIONAL', 'Kathmandu', 'Dubai',        '02:15', '05:45', '5 hrs 30 min',  55000, 300, 'Terminal 2', 'Gate B1'),
            ('FZ-A11', 'Flydubai',          'INTERNATIONAL', 'Kathmandu', 'Dubai',        '23:55', '03:25', '5 hrs 30 min',  42000, 189, 'Terminal 2', 'Gate B2'),
            ('RA-A21', 'Nepal Airlines',    'INTERNATIONAL', 'Kathmandu', 'Dubai',        '01:30', '05:00', '5 hrs 30 min',  48000, 140, 'Terminal 2', 'Gate B3'),

            # ── INTERNATIONAL — KATHMANDU → DOHA ──
            ('QR-B01', 'Qatar Airways',     'INTERNATIONAL', 'Kathmandu', 'Doha',         '03:00', '07:00', '5 hrs',         60000, 300, 'Terminal 2', 'Gate C1'),

            # ── INTERNATIONAL — KATHMANDU → KUALA LUMPUR ──
            ('MH-C01', 'Malaysia Airlines', 'INTERNATIONAL', 'Kathmandu', 'Kuala Lumpur', '00:30', '08:30', '5 hrs',         52000, 300, 'Terminal 2', 'Gate D1'),
            ('AK-C11', 'AirAsia',           'INTERNATIONAL', 'Kathmandu', 'Kuala Lumpur', '02:00', '10:00', '5 hrs',         38000, 180, 'Terminal 2', 'Gate D2'),

            # ── INTERNATIONAL — KATHMANDU → BANGKOK ──
            ('TG-D01', 'Thai Airways',      'INTERNATIONAL', 'Kathmandu', 'Bangkok',      '01:00', '06:30', '3 hrs 30 min',  45000, 300, 'Terminal 2', 'Gate E1'),
            ('FD-D11', 'Thai AirAsia',      'INTERNATIONAL', 'Kathmandu', 'Bangkok',      '23:30', '05:00', '3 hrs 30 min',  32000, 180, 'Terminal 2', 'Gate E2'),

            # ── INTERNATIONAL — KATHMANDU → SINGAPORE ──
            ('SQ-E01', 'Singapore Airlines','INTERNATIONAL', 'Kathmandu', 'Singapore',    '00:45', '07:45', '4 hrs',         70000, 280, 'Terminal 2', 'Gate F1'),
            ('TR-E11', 'Scoot',             'INTERNATIONAL', 'Kathmandu', 'Singapore',    '02:30', '09:30', '4 hrs',         40000, 180, 'Terminal 2', 'Gate F2'),

            # ── INTERNATIONAL — KATHMANDU → HONG KONG / TOKYO ──
            ('CX-F01', 'Cathay Pacific',    'INTERNATIONAL', 'Kathmandu', 'Hong Kong',    '01:15', '08:15', '5 hrs',         75000, 280, 'Terminal 2', 'Gate G1'),
            ('NH-G01', 'ANA',               'INTERNATIONAL', 'Kathmandu', 'Tokyo',        '00:30', '09:30', '6 hrs',         90000, 280, 'Terminal 2', 'Gate H1'),
        ]

        today = date.today()
        created = 0

        for (f_num, airline, f_type, from_city, to_city,
             dep_t, arr_t, duration, price, seats, terminal, gate) in flight_data:
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
