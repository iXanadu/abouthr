"""
Seed DriveDestination data for the Drive Time Calculator.

Usage:
    python manage.py seed_destinations
    python manage.py seed_destinations --clear  # Clear existing and re-seed
"""

from django.core.management.base import BaseCommand
from guide.models import DriveDestination


DESTINATIONS = [
    # Military Bases
    {
        'name': 'Naval Station Norfolk',
        'slug': 'naval-station-norfolk',
        'category': 'military',
        'address': '1530 Gilbert St, Norfolk, VA 23511',
        'latitude': 36.9465,
        'longitude': -76.3038,
        'order': 1,
    },
    {
        'name': 'Naval Air Station Oceana',
        'slug': 'nas-oceana',
        'category': 'military',
        'address': '1750 Tomcat Blvd, Virginia Beach, VA 23460',
        'latitude': 36.8207,
        'longitude': -76.0336,
        'order': 2,
    },
    {
        'name': 'Joint Base Langley-Eustis (Langley)',
        'slug': 'langley-afb',
        'category': 'military',
        'address': '45 Nealy Ave, Hampton, VA 23665',
        'latitude': 37.0832,
        'longitude': -76.3606,
        'order': 3,
    },
    {
        'name': 'Joint Base Langley-Eustis (Fort Eustis)',
        'slug': 'fort-eustis',
        'category': 'military',
        'address': '730 Washington Blvd, Fort Eustis, VA 23604',
        'latitude': 37.1439,
        'longitude': -76.5864,
        'order': 4,
    },
    {
        'name': 'Naval Medical Center Portsmouth',
        'slug': 'nmcp',
        'category': 'military',
        'address': '620 John Paul Jones Cir, Portsmouth, VA 23708',
        'latitude': 36.8469,
        'longitude': -76.3015,
        'order': 5,
    },
    {
        'name': 'Norfolk Naval Shipyard',
        'slug': 'norfolk-naval-shipyard',
        'category': 'military',
        'address': 'Portsmouth, VA 23709',
        'latitude': 36.8209,
        'longitude': -76.2961,
        'order': 6,
    },
    {
        'name': 'Naval Amphibious Base Little Creek',
        'slug': 'little-creek',
        'category': 'military',
        'address': '2600 Tarawa Ct, Virginia Beach, VA 23459',
        'latitude': 36.9176,
        'longitude': -76.1581,
        'order': 7,
    },
    {
        'name': 'Dam Neck Fleet Training Center',
        'slug': 'dam-neck',
        'category': 'military',
        'address': '1912 Regulus Ave, Virginia Beach, VA 23461',
        'latitude': 36.7738,
        'longitude': -75.9728,
        'order': 8,
    },
    {
        'name': 'Coast Guard Base Portsmouth',
        'slug': 'uscg-portsmouth',
        'category': 'military',
        'address': '4000 Coast Guard Blvd, Portsmouth, VA 23703',
        'latitude': 36.8331,
        'longitude': -76.3364,
        'order': 9,
    },
    {
        'name': 'Joint Expeditionary Base Little Creek-Fort Story',
        'slug': 'fort-story',
        'category': 'military',
        'address': 'Fort Story, VA 23459',
        'latitude': 36.9272,
        'longitude': -76.0117,
        'order': 10,
    },
    {
        'name': 'Naval Weapons Station Yorktown',
        'slug': 'nws-yorktown',
        'category': 'military',
        'address': 'Yorktown, VA 23691',
        'latitude': 37.2266,
        'longitude': -76.5478,
        'order': 11,
    },
    {
        'name': 'Oceana Naval Air Station Dam Neck Annex',
        'slug': 'oceana-dam-neck',
        'category': 'military',
        'address': 'Virginia Beach, VA 23461',
        'latitude': 36.7847,
        'longitude': -75.9771,
        'order': 12,
    },
    {
        'name': 'Naval Support Activity Hampton Roads',
        'slug': 'nsa-hampton-roads',
        'category': 'military',
        'address': '1968 Gilbert St, Norfolk, VA 23511',
        'latitude': 36.9448,
        'longitude': -76.3122,
        'order': 13,
    },
    {
        'name': 'Camp Peary (The Farm)',
        'slug': 'camp-peary',
        'category': 'military',
        'address': 'Williamsburg, VA 23188',
        'latitude': 37.3031,
        'longitude': -76.6775,
        'order': 14,
    },
    {
        'name': 'Naval Surface Warfare Center Dahlgren Division',
        'slug': 'nswc-dahlgren',
        'category': 'military',
        'address': '6149 Welsh Rd, Dahlgren, VA 22448',
        'latitude': 38.3342,
        'longitude': -77.0461,
        'order': 15,
    },
    {
        'name': 'NMCP Branch Medical Clinic',
        'slug': 'nmcp-clinic-oceana',
        'category': 'military',
        'address': '1935 Keflavik St, Virginia Beach, VA 23460',
        'latitude': 36.8217,
        'longitude': -76.0294,
        'order': 16,
    },

    # Airports
    {
        'name': 'Norfolk International Airport (ORF)',
        'slug': 'norfolk-airport-orf',
        'category': 'airport',
        'address': '2200 Norview Ave, Norfolk, VA 23518',
        'latitude': 36.8946,
        'longitude': -76.2012,
        'order': 1,
    },
    {
        'name': 'Newport News/Williamsburg International (PHF)',
        'slug': 'newport-news-airport-phf',
        'category': 'airport',
        'address': '900 Bland Blvd, Newport News, VA 23602',
        'latitude': 37.1319,
        'longitude': -76.4930,
        'order': 2,
    },
    {
        'name': 'Richmond International Airport (RIC)',
        'slug': 'richmond-airport-ric',
        'category': 'airport',
        'address': '1 Richard E Byrd Terminal Dr, Richmond, VA 23250',
        'latitude': 37.5052,
        'longitude': -77.3197,
        'order': 3,
    },

    # Hospitals
    {
        'name': 'Sentara Norfolk General Hospital',
        'slug': 'sentara-norfolk-general',
        'category': 'hospital',
        'address': '600 Gresham Dr, Norfolk, VA 23507',
        'latitude': 36.8615,
        'longitude': -76.3025,
        'order': 1,
    },
    {
        'name': "Children's Hospital of The King's Daughters (CHKD)",
        'slug': 'chkd',
        'category': 'hospital',
        'address': '601 Children\'s Ln, Norfolk, VA 23507',
        'latitude': 36.8601,
        'longitude': -76.3039,
        'order': 2,
    },
    {
        'name': 'Riverside Regional Medical Center',
        'slug': 'riverside-regional',
        'category': 'hospital',
        'address': '500 J Clyde Morris Blvd, Newport News, VA 23601',
        'latitude': 37.0576,
        'longitude': -76.4890,
        'order': 3,
    },
    {
        'name': 'Sentara Virginia Beach General Hospital',
        'slug': 'sentara-vb-general',
        'category': 'hospital',
        'address': '1060 First Colonial Rd, Virginia Beach, VA 23454',
        'latitude': 36.8510,
        'longitude': -76.0430,
        'order': 4,
    },
    {
        'name': 'Bon Secours Maryview Medical Center',
        'slug': 'maryview-medical',
        'category': 'hospital',
        'address': '3636 High St, Portsmouth, VA 23707',
        'latitude': 36.8360,
        'longitude': -76.3563,
        'order': 5,
    },
    {
        'name': 'Sentara Williamsburg Regional Medical Center',
        'slug': 'sentara-williamsburg',
        'category': 'hospital',
        'address': '100 Sentara Cir, Williamsburg, VA 23188',
        'latitude': 37.2879,
        'longitude': -76.7458,
        'order': 6,
    },
    {
        'name': 'Sentara CarePlex Hospital',
        'slug': 'sentara-careplex',
        'category': 'hospital',
        'address': '3000 Coliseum Dr, Hampton, VA 23666',
        'latitude': 37.0403,
        'longitude': -76.4024,
        'order': 7,
    },
    {
        'name': 'Chesapeake Regional Medical Center',
        'slug': 'chesapeake-regional',
        'category': 'hospital',
        'address': '736 Battlefield Blvd N, Chesapeake, VA 23320',
        'latitude': 36.7608,
        'longitude': -76.2386,
        'order': 8,
    },

    # Universities
    {
        'name': 'Old Dominion University',
        'slug': 'old-dominion-university',
        'category': 'university',
        'address': '5115 Hampton Blvd, Norfolk, VA 23529',
        'latitude': 36.8851,
        'longitude': -76.3055,
        'order': 1,
    },
    {
        'name': 'Norfolk State University',
        'slug': 'norfolk-state-university',
        'category': 'university',
        'address': '700 Park Ave, Norfolk, VA 23504',
        'latitude': 36.8477,
        'longitude': -76.2676,
        'order': 2,
    },
    {
        'name': 'College of William & Mary',
        'slug': 'william-and-mary',
        'category': 'university',
        'address': '200 Stadium Dr, Williamsburg, VA 23185',
        'latitude': 37.2708,
        'longitude': -76.7071,
        'order': 3,
    },
    {
        'name': 'Christopher Newport University',
        'slug': 'cnu',
        'category': 'university',
        'address': '1 Avenue of the Arts, Newport News, VA 23606',
        'latitude': 37.0631,
        'longitude': -76.4935,
        'order': 4,
    },
    {
        'name': 'Tidewater Community College',
        'slug': 'tcc',
        'category': 'university',
        'address': '300 Granby St, Norfolk, VA 23510',
        'latitude': 36.8570,
        'longitude': -76.2882,
        'order': 5,
    },
    {
        'name': 'Regent University',
        'slug': 'regent-university',
        'category': 'university',
        'address': '1000 Regent University Dr, Virginia Beach, VA 23464',
        'latitude': 36.7937,
        'longitude': -76.1214,
        'order': 6,
    },

    # Beaches
    {
        'name': 'Virginia Beach Oceanfront',
        'slug': 'virginia-beach-oceanfront',
        'category': 'beach',
        'address': '2100 Parks Ave, Virginia Beach, VA 23451',
        'latitude': 36.8529,
        'longitude': -75.9780,
        'order': 1,
    },
    {
        'name': 'Sandbridge Beach',
        'slug': 'sandbridge-beach',
        'category': 'beach',
        'address': 'Sandbridge Rd, Virginia Beach, VA 23456',
        'latitude': 36.7201,
        'longitude': -75.9329,
        'order': 2,
    },
    {
        'name': 'Buckroe Beach',
        'slug': 'buckroe-beach',
        'category': 'beach',
        'address': '100 S 1st St, Hampton, VA 23664',
        'latitude': 37.0327,
        'longitude': -76.3006,
        'order': 3,
    },
    {
        'name': 'Ocean View Beach',
        'slug': 'ocean-view-beach',
        'category': 'beach',
        'address': '400 W Ocean View Ave, Norfolk, VA 23503',
        'latitude': 36.9395,
        'longitude': -76.2636,
        'order': 4,
    },
    {
        'name': 'First Landing State Park',
        'slug': 'first-landing-state-park',
        'category': 'beach',
        'address': '2500 Shore Dr, Virginia Beach, VA 23451',
        'latitude': 36.9168,
        'longitude': -76.0461,
        'order': 5,
    },
    {
        'name': 'Chic\'s Beach',
        'slug': 'chics-beach',
        'category': 'beach',
        'address': 'E Ocean View Ave, Norfolk, VA 23503',
        'latitude': 36.9387,
        'longitude': -76.0963,
        'order': 6,
    },
]


class Command(BaseCommand):
    help = 'Seed initial DriveDestination data for the Drive Time Calculator'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing destinations before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = DriveDestination.objects.all().delete()[0]
            self.stdout.write(f'Cleared {deleted_count} existing destinations')

        created_count = 0
        updated_count = 0

        for dest_data in DESTINATIONS:
            dest, created = DriveDestination.objects.update_or_create(
                slug=dest_data['slug'],
                defaults=dest_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded destinations: {created_count} created, {updated_count} updated'
            )
        )
