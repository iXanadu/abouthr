"""
Seed data management command for About Hampton Roads.
Seeds all content from the PDF relocation guide.
"""

from django.core.management.base import BaseCommand
from guide.models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember
)


class Command(BaseCommand):
    help = 'Seeds the database with Hampton Roads relocation guide content'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Clear existing data (optional - comment out if you want to preserve)
        self.stdout.write('Clearing existing data...')
        Venue.objects.all().delete()
        VendorUtility.objects.all().delete()
        MilitaryBase.objects.all().delete()
        Tunnel.objects.all().delete()
        VacationDestination.objects.all().delete()
        Testimonial.objects.all().delete()
        TeamMember.objects.all().delete()
        City.objects.all().delete()
        Region.objects.all().delete()

        # Seed in order
        self.seed_regions()
        self.seed_cities()
        self.seed_venues()
        self.seed_military_bases()
        self.seed_tunnels()
        self.seed_vacation_destinations()
        self.seed_vendor_utilities()
        self.seed_testimonials()
        self.seed_team_members()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def seed_regions(self):
        self.stdout.write('  Seeding regions...')

        Region.objects.create(
            name='Southside',
            slug='southside',
            description='The Southside of Hampton Roads includes Virginia Beach, Chesapeake, Norfolk, Portsmouth, Suffolk, and Smithfield - located south of the James River.',
            order=1
        )

        Region.objects.create(
            name='Peninsula',
            slug='peninsula',
            description='The Peninsula of Hampton Roads includes Hampton, Newport News, and Williamsburg/Yorktown - located north of the James River.',
            order=2
        )

        self.stdout.write(f'    Created {Region.objects.count()} regions')

    def seed_cities(self):
        self.stdout.write('  Seeding cities...')

        southside = Region.objects.get(slug='southside')
        peninsula = Region.objects.get(slug='peninsula')

        cities_data = [
            # Southside cities
            {
                'name': 'Virginia Beach',
                'slug': 'virginia-beach',
                'region': southside,
                'description': '''Located along the Atlantic Ocean and Chesapeake Bay, Virginia Beach epitomizes coastal living. As Virginia's largest populated city, it couples a distinctive blend of easygoing beach atmosphere with all the amenities of big-city living. Life here has the best combination of quiet suburbia and vibrant nightlife. There are miles of boardwalk and beach access, a vibrant financial and retail district, one of the best public school systems in the nation and distinctive cultural attractions and entertainment options. The city's significant military presence, a bustling tourism industry, active community engagement, and a moderate coastal climate all contribute to the appeal of living in this beautiful city.''',
                'has_beaches': True,
                'order': 1,
            },
            {
                'name': 'Chesapeake',
                'slug': 'chesapeake',
                'region': southside,
                'description': '''Situated on the Atlantic Intracoastal Waterway, Chesapeake offers an endless range of outdoor activities, terrific shopping, phenomenal food, and beautiful wildlife. Nestled amidst stunning natural landscapes, including parks and forests like Oak Grove and Northwest River Park, and the expansive Great Dismal Swamp Nature Preserve, the city offers a haven for outdoor enthusiasts with activities like hiking, birdwatching, and kayaking. Chesapeake also offers close proximity to the more major cities, providing easy access to big-city amenities while preserving a quieter, suburban lifestyle. Moreover, Chesapeake's growing economy and varied job opportunities attract professionals seeking a balance between work and a high quality of life, further enhancing its appeal as a place where nature, community, and opportunity seamlessly intersect.''',
                'has_beaches': False,
                'order': 2,
            },
            {
                'name': 'Norfolk',
                'slug': 'norfolk',
                'region': southside,
                'description': '''This eclectic city nestled against the Chesapeake Bay shines for many reasons. Its historical significance as a maritime hub, anchored by the world's largest naval base, NoB, infuses the city with a unique sense of pride and heritage. The blend of old and new in its neighborhoods create a vibrant tapestry, from the trendy Ghent district with its artistic flair to historic districts that preserve the city's roots. The culinary scene is a rich owner-operated melting pot of diverse cuisines for every palate! And with options like Norfolk Botanical Gardens, the Chrysler Museum of Art, and the always-fun Waterside district, there are endless entertainment options for both adults and families alike!''',
                'has_beaches': False,
                'order': 3,
            },
            {
                'name': 'Portsmouth',
                'slug': 'portsmouth',
                'region': southside,
                'description': '''Founded in 1752, the town of Portsmouth sits proudly along the banks of the Elizabeth River, which has been a lifeline for commerce and trade since its inception. This city is home to the integral Naval Shipyard, with 800 waterfront acres dedicated solely to maintaining our U.S. Navy's massive fleet. This historic community is also known for its diverse attractions, shops, and restaurants. With several charming historic districts and vibrant visual & musical arts scene, this area is filled with unique character and a constantly evolving economy.''',
                'has_beaches': False,
                'order': 4,
            },
            {
                'name': 'Suffolk',
                'slug': 'suffolk',
                'region': southside,
                'description': '''Nestled in southwest Hampton Roads, life in Suffolk is a beautiful blend of southern hospitality, scenic beauty, and a close-knit community. With sprawling farmlands, pristine waterways, and a rich history that dates back centuries, Suffolk has a unique charm that captures the essence of a tranquil yet economically thriving southern town. Savor locally grown produce, meander through historic districts, and experience the peace of a slower pace of life that this thriving city has to offer.''',
                'has_beaches': False,
                'order': 5,
            },
            {
                'name': 'Smithfield',
                'slug': 'smithfield',
                'region': southside,
                'description': '''Characterized by its historical ambiance and small-town charm, this town boasts well-preserved Colonial and Victorian architecture, creating a picturesque atmosphere. Smithfield's tight-knit community fosters a strong sense of togetherness, with numerous local events and festivals throughout the year. Outdoor enthusiasts can enjoy activities along the Pagan and James Rivers, while food lovers can savor the famous Smithfield Ham and other southern cuisine in local restaurants and at the weekly farmer's markets. Enjoy peaceful rural living with easy access to nearby cities like Newport News and Norfolk for entertainment & employment opportunities!''',
                'has_beaches': False,
                'order': 6,
            },
            # Peninsula cities
            {
                'name': 'Hampton',
                'slug': 'hampton',
                'region': peninsula,
                'description': '''Located along the Chesapeake Bay, the city of Hampton offers a comfortable quality of life with a cost of living that is often lower than in some larger urban areas. Residents can enjoy a mix of modern amenities and centuries-old historic charm. With high-profile landmarks like the Hampton Coliseum, Hampton University, NASA's Langley Research Center, Langley Air Force Base, and Historic Ft. Monroe, Hampton is a powerhouse for economic contribution, entertainment and educational opportunities.''',
                'has_beaches': True,
                'order': 7,
            },
            {
                'name': 'Newport News',
                'slug': 'newport-news',
                'region': peninsula,
                'description': '''This city holds historical significance as the home of Newport News Shipbuilding, a monumental shipyard with roots tracing back to the late 19th century. With a diverse economy encompassing shipbuilding, aerospace, manufacturing, healthcare, education, and military installations including Joint Base Langley-Eustis, this city offers residents a wide range of employment opportunities. The presence of Christopher Newport University (CNU) contributes to the city's academic landscape and cultural vibrancy. Situated along the James River and Chesapeake Bay, there are also endless opportunities for outdoor activities, from hiking to boating. The city's thriving cultural and arts scene, strong community engagement, and comfortable quality of life make it an enticing place to call home.''',
                'has_beaches': False,
                'order': 8,
            },
            {
                'name': 'Williamsburg & Yorktown',
                'slug': 'williamsburg-yorktown',
                'region': peninsula,
                'description': '''Williamsburg & Yorktown offer an unmatched blend of national historic significance, academic excellence, and natural beauty. Founded in 1632, these two cities are renowned for their Colonial Historic Areas, where residents can step into rich living history with original cobblestone streets, monuments, museums, reenactments and buildings that witnessed our founding fathers and the birth of the 'New World'. Williamsburg is also home to the prestigious College of William & Mary, and Busch Gardens Amusement Park, while Yorktown is renowned for its equally rich history and nationally recognized school districts. Rooted along the James River and in proximity to absolutely beautiful state parks, outdoor enthusiasts have endless recreational opportunities here. With a welcoming community spirit and a calendar filled with cultural events, these treasured cities offer a unique lifestyle deeply rooted in both the past and the present.''',
                'has_beaches': True,
                'order': 9,
            },
        ]

        for city_data in cities_data:
            City.objects.create(**city_data)

        self.stdout.write(f'    Created {City.objects.count()} cities')

    def seed_venues(self):
        self.stdout.write('  Seeding venues...')

        # Get all cities
        virginia_beach = City.objects.get(slug='virginia-beach')
        chesapeake = City.objects.get(slug='chesapeake')
        norfolk = City.objects.get(slug='norfolk')
        portsmouth = City.objects.get(slug='portsmouth')
        suffolk = City.objects.get(slug='suffolk')
        smithfield = City.objects.get(slug='smithfield')
        hampton = City.objects.get(slug='hampton')
        newport_news = City.objects.get(slug='newport-news')
        williamsburg = City.objects.get(slug='williamsburg-yorktown')

        venues_data = []

        # VIRGINIA BEACH
        # Restaurants
        vb_restaurants = [
            'The Bee and the Biscuit', 'Hot Tuna', 'Bay Local', "Waterman's",
            'Atlantic on Pacific', 'Craft Burger Bar', "The Butcher's Son",
            "Steinhilber's", "Orion's Roof", 'Chicks Oyster Bar', "Doc Taylor's",
            'Shorebreak Pizza', "Mannino's Italian", 'The Porch on Long Creek'
        ]
        for name in vb_restaurants:
            venues_data.append({'city': virginia_beach, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        vb_cafes = [
            '7 Hands Coffee', 'Three Ships Coffee', 'Java Surf', 'Bad Ass Coffee of Hawaii',
            'Roast Rider', 'The Green Cat Juice Bar & Market', 'Back Bay Farmhouse Brewery',
            'Pleasure House Brewing', 'New Realm Brewing Co.', 'Wasserhund Brewing',
            'Smartmouth Brewing', 'Chesapeake Bay Distillery'
        ]
        for name in vb_cafes:
            venues_data.append({'city': virginia_beach, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        vb_attractions = [
            'King Neptune Statue', 'First Landing State Park', 'VB Aquarium',
            'VB Amphitheater Concert Venue', 'Ocean Breeze Waterpark',
            'First Landing (AKA Seashore State Park)', 'Mt Trashmore Park',
            'Virginia Museum of Contemporary Art', 'Virginia Beach Farmer\'s Market',
            'Old Beach Farmers & Vintage Market', 'Hunt Club Farm', 'ViBe District',
            'Towne Center', 'Munden Point Park', 'Funny Bone Comedy Club',
            'Stumpy Lake Natural Area', "Edgar Cayce's A.R.E.", 'Grommet Island',
            'The Virginia Beach Fishing Pier', 'Naval Aviation Monument Park',
            'Virginia Beach KOA Campground', 'The Adventure Park', 'Woodstock Park',
            'Q-Masters Billiards', 'APex Indoor Entertainment',
            'iFly Indoor Skydiving Simulator', 'Latitudes Indoor Rock Climbing'
        ]
        for name in vb_attractions:
            venues_data.append({'city': virginia_beach, 'venue_type': 'attraction', 'name': name})

        # Events
        vb_events = [
            'Something In The Water', 'Neptune Festival', 'Boardwalk Art Show',
            'VB Polar Plunge', 'Beach Music Weekend', 'Holiday Parade at the Beach',
            "McDonald's Holiday Lights on the Boardwalk", 'Yuengling Shamrock Festival and 8k',
            'Coastal VA Wine Fest', 'East Coast Surfing Championship'
        ]
        for name in vb_events:
            venues_data.append({'city': virginia_beach, 'venue_type': 'event', 'name': name})

        # Beaches
        vb_beaches = [
            {'name': 'Va. Beach Oceanfront', 'address': '1700 Atlantic Ave'},
            {'name': '1st Street Jetty', 'address': '100 2nd Street'},
            {'name': 'Croatan', 'address': '920 Vanderbilt Ave'},
            {'name': 'North End', 'address': '40th St - 89th Street'},
            {'name': 'Chics Beach', 'address': '4536 Ocean View Ave'},
            {'name': 'Sandbridge', 'address': '2500 Sandfiddler Road'},
        ]
        for beach in vb_beaches:
            venues_data.append({
                'city': virginia_beach, 'venue_type': 'beach',
                'name': beach['name'], 'address': beach['address']
            })

        # CHESAPEAKE
        # Restaurants
        chesapeake_restaurants = [
            'Amber Lantern', 'Cutlass Grille', 'Pizzeria Bella Vista', "The Butcher's Son",
            'Lockside Bar & Grille', "Warrior's Mongolian", 'Luce Segundo', 'The BBQ Shack',
            'Inaka Sushi', 'Abuelos Mexican', 'The Egg Bistro', 'Cork & Bull Chophouse',
            'YNOT Italian', 'Geisha Japanese Steakhouse', "Famous Uncle Al's Hot Dogs",
            "Kelly's Tavern", 'Taste', 'Windy City Pizza', 'Wickers Crab Pot'
        ]
        for name in chesapeake_restaurants:
            venues_data.append({'city': chesapeake, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        chesapeake_cafes = [
            'The Garage Brewery', 'Wasserhund Brewing Company', 'Big Ugly Brewing',
            'Studly Brewing', 'Tap It Local', 'Hickory Trading Company', "Zeke's",
            'Sun Flour Cafe', 'Einstein Brothers Bagels and Coffee', 'Gather Cafe',
            'Pale Horse Coffee'
        ]
        for name in chesapeake_cafes:
            venues_data.append({'city': chesapeake, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        chesapeake_attractions = [
            'Historic Greenbrier Farms', "Bergey's Breadbasket & Farm", 'City View Park',
            'Chesapeake City Park', 'Oak Grove Park', 'Deep Creek Lock Park',
            'Chesapeake Arboretum', 'Chesapeake Planetarium', 'Northwest River Park',
            'Great Dismal Swamp National Wildlife Refuge', 'Chesapeake & Albemarle Canal',
            'Mount Pleasant Farms', 'Skyzone Trampoline Park'
        ]
        for name in chesapeake_attractions:
            venues_data.append({'city': chesapeake, 'venue_type': 'attraction', 'name': name})

        # Events
        chesapeake_events = [
            'Oyster & South Festival', 'Chesapeake Wine Festival', 'Chesapeake Jubilee',
            'Symphony Under the Stars', 'Battle of Great Bridge', 'KayaXpedition',
            'Virginia Arts Festival', "Chesapeake Farmers' Market", 'Chesapeake Art Walk',
            'Great American Food Fest'
        ]
        for name in chesapeake_events:
            venues_data.append({'city': chesapeake, 'venue_type': 'event', 'name': name})

        # NORFOLK
        # Restaurants
        norfolk_restaurants = [
            'Luce', 'Yorgos Bageldashery', 'Mymar Poke & Grill', 'Doumars Ice Cream & BBQ',
            'Saltine', "Hell's Kitchen", "Grace O'Malley's Irish Pub", 'Freemason Abbey',
            'Handsome Biscuit', 'Codex', 'No Frill Bar & Grill', 'The Ten Top', "Omar's",
            'Orapax', 'Union Taco', 'Norfolk Seafood Co.'
        ]
        for name in norfolk_restaurants:
            venues_data.append({'city': norfolk, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        norfolk_cafes = [
            'Smartmouth Brewing Company', 'Afterglow Brewing', 'Cova Brewing Co.',
            'Vessel Craft Coffee', 'Three Ships Coffee', 'Coaster Coffee', 'Cafe Milo'
        ]
        for name in norfolk_cafes:
            venues_data.append({'city': norfolk, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        norfolk_attractions = [
            'NoB Naval Station', 'Norfolk Scope', 'Towne Point Park', 'Nauticus',
            'Chrysler Museum of Art', 'Heritage Cannonball Trail', 'Hermitage Museum & Gardens',
            'Harrison Opera House', 'The Virginia Zoo', 'Elizabeth River Trail',
            'Norfolk Botanical Gardens', 'Nauticus & Battleship Wisconsin',
            'Norfolk Premium Outlets', 'Ocean View Fishing Pier', 'The NorVA',
            'Wells Theatre', 'Attucks Theater', 'Norfolk Admirals Hockey',
            'Norfolk Tides Baseball', 'Fort Norfolk', 'Ocean View Pier', 'East Beach Marina',
            'Waterside District', 'Neon District', 'Granby Street', 'Downtown Norfolk',
            'Ghent District', 'Ocean View Beach'
        ]
        for name in norfolk_attractions:
            venues_data.append({'city': norfolk, 'venue_type': 'attraction', 'name': name})

        # Events
        norfolk_events = [
            'Norfolk Harborfest', 'Cigar Festival', "VA Children's Festival",
            'The Patriotic Festival', 'Virginia Arts Festival'
        ]
        for name in norfolk_events:
            venues_data.append({'city': norfolk, 'venue_type': 'event', 'name': name})

        # PORTSMOUTH
        # Restaurants
        portsmouth_restaurants = [
            'Gosport Tavern', 'Five Boroughs Restaurant', 'Lobscouser Restaurant',
            'Yoolks On Us', 'District', 'Fish & Slips Marina Raw Bar & Grill',
            'Longboards Olde Towne', 'Thyme on the River', 'Olde Towne Public House',
            'Guads Mexican', 'Vietnam 81', 'Still Worldly Eclectic Tapas', 'The Pizza Box'
        ]
        for name in portsmouth_restaurants:
            venues_data.append({'city': portsmouth, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        portsmouth_cafes = [
            'The Coffee Shoppe', 'Cure', "JoJack's Espresso Bar & Cafe",
            'Tidewater Coffee Inc.', 'Gardner Willz Cafe', 'The Book Club LLC',
            'Post Secondary Brewing Co.', 'MoMac Brewing Co.', 'Harbor Trail Brewing Co.',
            'The Bier Garden', 'Benchtop Brewing Co.'
        ]
        for name in portsmouth_cafes:
            venues_data.append({'city': portsmouth, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        portsmouth_attractions = [
            "Children's Museum", 'Portsmouth Pavilion', 'Commodore Theatre',
            'Portsmouth Naval Shipyard Museum', 'Olde Towne Historic District',
            'Elizabeth River Ferry', 'Olde Towne Farmers Market',
            'Virginia Sports Hall of Fame and Museum', 'Lightship Museum',
            "Historic St. Paul's Church"
        ]
        for name in portsmouth_attractions:
            venues_data.append({'city': portsmouth, 'venue_type': 'attraction', 'name': name})

        # Events
        portsmouth_events = [
            'The Path of History Tour in Olde Towne Portsmouth', 'River Days Festival',
            'Portsmouth Invitational Tournament', 'Portsmouth Beer Stroll',
            'Christmas in the Park', 'Portsmouth Seafood Festival',
            'Portsmouth Music Festival', 'Portsmouth Memorial Day Parade',
            'Portsmouth Seawall Art Show'
        ]
        for name in portsmouth_events:
            venues_data.append({'city': portsmouth, 'venue_type': 'event', 'name': name})

        # SUFFOLK
        # Restaurants
        suffolk_restaurants = [
            "Harper's Table", "Decoy's", 'Sushi Aka', 'Vintage Tavern',
            "Mason's Grill and Smokehouse", 'High Tide Restaurant & Raw Bar',
            "Amedeo's Ristorante", 'The Mod Olive', "Amici's Pizza Cafe", "Baron's Pub",
            'Fin & Tonic', 'Decent People Taproom', 'Cazadores Mexican Restaurant',
            'Country Boys BBQ', "Danny's Downtown Dogs", 'River Stone Chophouse'
        ]
        for name in suffolk_restaurants:
            venues_data.append({'city': suffolk, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        suffolk_cafes = [
            'Nansemond Brewing Station', 'Decent People Taproom', 'Elation Brewing',
            'Great Bottles', 'Haven and Hull', 'Cafe DaVina', 'Brighter Day Cafe',
            'Knotts Coffee Company', 'Nutrition Ignition', 'Wall Street Cafe'
        ]
        for name in suffolk_cafes:
            venues_data.append({'city': suffolk, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        suffolk_attractions = [
            'Suffolk Center for Cultural Arts', 'Knot Hole Station', 'Historic Downtown Suffolk',
            'Skydive Suffolk', 'Bridgeport Center', 'Bennetts Creek Park',
            "Riddick's Folly House Museum", 'Suffolk Art Gallery',
            'Seaboard Station Railroad Museum', "Planter's Peanut Store",
            'The Historic Obici House', "Fireflies on Bennett's Creek",
            'The Pinner House B&B'
        ]
        for name in suffolk_attractions:
            venues_data.append({'city': suffolk, 'venue_type': 'attraction', 'name': name})

        # Events
        suffolk_events = [
            'Driver Days Festivals', 'Suffolk Peanut Festival', "Bennett's Creek Kayak Excursion",
            'Taste of Suffolk Downtown Street Festival', 'Plein Air Festival',
            'Legends of Main Street: A Suffolk Ghost Walk'
        ]
        for name in suffolk_events:
            venues_data.append({'city': suffolk, 'venue_type': 'event', 'name': name})

        # SMITHFIELD
        # Restaurants
        smithfield_restaurants = [
            'Smithfield Station', "Captain Chuck-a-Muck's", "Amedeo's Ristorante",
            'Taste of Smithfield', "Paul's Deli & Neighborhood Restaurant",
            'Mi Casita Mexican Restaurant', "Farmer's Table", 'Sodosopa',
            'The Cockeyed Rooster', 'Tokyo Thai', "Q Daddy's Pitmaster BBQ",
            'Historic Smithfield Inn', 'Smithfield Ice Cream Parlor',
            'Smithfield Gourmet Bakery'
        ]
        for name in smithfield_restaurants:
            venues_data.append({'city': smithfield, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        smithfield_cafes = [
            'Wharf Hill Brewing Company', 'Red Point Taphouse', 'The William Rand Tavern',
            'Java 39', 'Cafe Place', 'Cure Coffeehouse', 'Tea-Tonic Tearoom'
        ]
        for name in smithfield_cafes:
            venues_data.append({'city': smithfield, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        smithfield_attractions = [
            'Smithfield Station', 'The Mansion on Main B&B', 'Windsor Castle Park',
            "Smithfield Farmer's Market", 'Historic Main Street', 'Isle of Wight County Museum',
            'Historic Fort Huger', "St. Luke's Historic Church & Museum",
            'Cypress Creek Golf Club', 'Smithfield Dragway', 'Artisans Center of Virginia'
        ]
        for name in smithfield_attractions:
            venues_data.append({'city': smithfield, 'venue_type': 'attraction', 'name': name})

        # Events
        smithfield_events = [
            'Smithfield Farmers Market', 'Smithfield BOB Fest',
            'Genuine Bacon & Bourbon Music Fest', 'Manor House Dinner Club Events',
            'Bacchus Wine & Food Festival', 'Smithfield VA Wine & Brew Fest',
            'Peanut Fest', 'Christmas in Smithfield', 'Smithfield Music Spring Concert Series',
            'Smithfield Wine & Brew Fest', 'Smithfield Olden Days Festival',
            'Isle of Wight County Fair'
        ]
        for name in smithfield_events:
            venues_data.append({'city': smithfield, 'venue_type': 'event', 'name': name})

        # HAMPTON
        # Restaurants
        hampton_restaurants = [
            'First Watch', 'Marker 20', 'Baked Bistro & Pizza', 'The Deadrise',
            'Venture Kitchen & Raw Bar', 'Pour Girls', 'The Grey Goose',
            'County Grill & Smokehouse', 'Cyprus Grille', 'Cibus Chophouse',
            "The Baker's Wife Bistro & Bar", 'Mezcal Mexican Grille & Restaurant',
            "Mama Rosa's Italian", 'Mill Creek Tavern', 'Musasi Japanese Restaurant'
        ]
        for name in hampton_restaurants:
            venues_data.append({'city': hampton, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        hampton_cafes = [
            'Bull Island Brewing Co.', 'St. George Brewing Co.', 'Capstan Bar Brewing Co.',
            'The Vanguard Brewpub & Distillery', 'Sly Clyde Ciderworks', '1865 Brewing Co.',
            'Oozlefinch Beers & Blending', 'Sweet Beans Coffee Bar', 'Fika Coffeehouse',
            'Firehouse Coffee 1881', "Momo's Cafe"
        ]
        for name in hampton_cafes:
            venues_data.append({'city': hampton, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        hampton_attractions = [
            'Langley Research Visitor Center', 'Hampton University', 'Phoebus Historic District',
            'Sandy Bottom Nature Park', 'Hampton National Cemetery', 'Hampton Maritime Center',
            'Bluebird Gap Farm', 'Mill Point Park', 'Fort Monroe National Monument',
            'Old Point Comfort Lighthouse', 'Hampton History Museum',
            "NASA's Virginia Air & Space Science Center", 'Buckroe Beach',
            'Hampton Coliseum', 'Hampton Carousel', 'Hampton Roads Convention Center'
        ]
        for name in hampton_attractions:
            venues_data.append({'city': hampton, 'venue_type': 'attraction', 'name': name})

        # Events
        hampton_events = [
            'Hampton Coliseum Gun Show', 'Hampton Cup Regatta', 'Hampton Roads Soul Music Festival',
            'Hampton Roads International Auto Show', 'Hampton Roads Tattoo Arts Festival',
            "Hampton History Museum's Black History Month Celebration", 'Jazz Festival',
            'Blackbeard Pirate Festival', 'Heritage Day Festival', 'Bay Days',
            'Hampton Blues Festival', 'Hampton Horror Tours', 'Holly Days Parade', 'Holiday Market'
        ]
        for name in hampton_events:
            venues_data.append({'city': hampton, 'venue_type': 'event', 'name': name})

        # Beaches
        hampton_beaches = [
            {'name': 'Buckroe Beach', 'address': 'Buckroe Beach, Hampton, VA'},
        ]
        for beach in hampton_beaches:
            venues_data.append({
                'city': hampton, 'venue_type': 'beach',
                'name': beach['name'], 'address': beach['address']
            })

        # NEWPORT NEWS
        # Restaurants
        newport_news_restaurants = [
            "Schooner's Grill", "Harpoon Larry's Fish House & Oyster Bar",
            "Cheddar's Scratch Kitchen", 'Second Street American bistro', 'Fin Seafood',
            'Smoke BBQ', 'Saffron', 'Cove Tavern', 'Saisaki Asian Bistro', "Farmer's Table",
            'Al Fresco', "BJ's Restaurant & Brewhouse", 'Tida Thai Cuisine',
            'Mr. Boil Cajun Seafood & Poke Bowls', 'De Rican Chef', 'Burger Theory',
            "Gus's New York Pizza"
        ]
        for name in newport_news_restaurants:
            venues_data.append({'city': newport_news, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        newport_news_cafes = [
            'Grounded Coffee', 'Cure Coffeehouse', "Angie's Coffee", 'Coffee Beanery',
            '7 Brew Coffee', 'Hilton Tavern Brewing Co.', 'Beervana Taphouse',
            'Tradition Brewing Co.', 'Coastal Fermatory', 'Ironclad Distillery',
            'Blind Girl Bottle Shop'
        ]
        for name in newport_news_cafes:
            venues_data.append({'city': newport_news, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        newport_news_attractions = [
            "The Mariner's Museum and Park", 'Newport News Park', "Huntington Park & Lion's Bridge",
            'Virginia Living Museum', 'The Peninsula Fine Arts Center', 'Peninsula SPCA & Petting Zoo',
            'Endview Plantation', 'Lee Hall Mansion', 'Newport News Golf Club at Deer Run',
            'Warwick Towne Center', 'Ferguson Center for the Arts', 'King-Lincoln Park',
            'Newport News Public Art Foundation', 'Newport News Golf Club at Kiln Creek',
            'City Center at Oyster Point', 'Historic Hilton Village'
        ]
        for name in newport_news_attractions:
            venues_data.append({'city': newport_news, 'venue_type': 'attraction', 'name': name})

        # Events
        newport_news_events = [
            'One City Marathon', 'Festival of Lights at Newport News Park',
            'Celebration in Lights 5K', 'Newport News Fall Festival of Folklife',
            'Newport News Greek Festival', "Newport News Children's Festival of Friends",
            'Battle of Hampton Roads Weekend', 'Bacchus Wine & Food Festival',
            'Hilton Village Spring Festival', 'African Landing Day Commemoration',
            'Harvest Faire at Endview Plantation', 'Newport News Arts Festival',
            "Shrimpfest at St. George's Episcopal Church", 'Jazz on the James',
            'Newport News Spring Festival of Art'
        ]
        for name in newport_news_events:
            venues_data.append({'city': newport_news, 'venue_type': 'event', 'name': name})

        # WILLIAMSBURG & YORKTOWN
        # Restaurants
        williamsburg_restaurants = [
            'Food for Thought', 'Le Yaca French Restaurant', 'Fat Canary',
            "King's Arms Tavern", 'Amber Ox Public House', 'Blue Talon Bistro',
            "The Hound's Tale", "Rick's Cheese Steak Shop", 'Old Chickahominy House',
            'Waypoint Seafood & Grille', "Berret's Seafood", 'Mellow Mushroom Pizza',
            'Rockefeller Room', 'Cochon on 2nd', 'Another Broken Egg Cafe',
            'Electric Circus Taco Bar', 'Riverwalk Restaurant', 'Carrot Tree Kitchens',
            'Yorktown Pub', 'The Gallery at York Hall', 'Water Street Grille'
        ]
        for name in williamsburg_restaurants:
            venues_data.append({'city': williamsburg, 'venue_type': 'restaurant', 'name': name})

        # Cafes & Breweries
        williamsburg_cafes = [
            'Copper Fox Distillery', 'The Virginia Beer Company', 'Precarious Beer Project',
            'Strangeways Brewing', 'Aleworks', 'Billsburg Brewery',
            '8 Shires Coloniale Distillery', "Larry's Alehouse", 'Tipsy Bean Cafe',
            'Illy Cafe', '1607 Coffee Company', 'Column 15 Coffee', 'Mobjack Bay Coffee',
            'Yorktown Market Days'
        ]
        for name in williamsburg_cafes:
            venues_data.append({'city': williamsburg, 'venue_type': 'cafe_brewery', 'name': name})

        # Attractions
        williamsburg_attractions = [
            'Busch Gardens', 'Water Country USA', 'Go Ape Zipline & Treetop Adventure Experience',
            'Ripleys Believe It or Not! Williamsburg', 'Williamsburg Outlets',
            'Colonial Williamsburg', 'Jamestown Settlement', 'College of William & Mary',
            'The DeWitt Wallace Decorative Arts Museum', 'Abby Aldrich Rockefeller Folk Art Museum',
            "Governor's Palace", 'Williamsburg Winery', 'Bassett Hall', 'Waller Mill Park',
            'The Virginia Capitol Building', 'Art Museums of Colonial Williamsburg',
            'York River State Park', 'Yorktown Beach', 'Colonial National Historical Park',
            'Riverwalk Landing'
        ]
        for name in williamsburg_attractions:
            venues_data.append({'city': williamsburg, 'venue_type': 'attraction', 'name': name})

        # Events
        williamsburg_events = [
            'Grand Illumination', 'Colonial Williamsburg Garden Symposium',
            'Williamsburg Farmers Market', 'Williamsburg Craft Beer Festival',
            'Williamsburg Film Festival', 'Retro Williamsburg', 'Williamsburg Fall Arts Festival',
            'Blues, Brews & BBQ Festival', 'Williamsburg Symphony Orchestra Concerts',
            'Williamsburg Book Festival', 'Williamsburg Christmas Parade',
            'Williamsburg Taste Festival', 'Contemporary Arts Festival',
            'Williamsburg Christmas Market', 'Yorktown Day', 'Yorktown Wine Festival',
            'Pirate Invasion Weekend', 'Virginia Symphony Concert', 'Rhythms on the Riverwalk'
        ]
        for name in williamsburg_events:
            venues_data.append({'city': williamsburg, 'venue_type': 'event', 'name': name})

        # Beaches
        williamsburg_beaches = [
            {'name': 'Yorktown Beach', 'address': 'Yorktown Beach, Yorktown, VA'},
        ]
        for beach in williamsburg_beaches:
            venues_data.append({
                'city': williamsburg, 'venue_type': 'beach',
                'name': beach['name'], 'address': beach['address']
            })

        # Create all venues
        for i, venue_data in enumerate(venues_data):
            Venue.objects.create(order=i, **venue_data)

        self.stdout.write(f'    Created {Venue.objects.count()} venues')

    def seed_military_bases(self):
        self.stdout.write('  Seeding military bases...')

        norfolk = City.objects.get(slug='norfolk')
        portsmouth = City.objects.get(slug='portsmouth')
        virginia_beach = City.objects.get(slug='virginia-beach')
        hampton = City.objects.get(slug='hampton')
        newport_news = City.objects.get(slug='newport-news')
        williamsburg = City.objects.get(slug='williamsburg-yorktown')

        bases_data = [
            # Navy
            {'name': 'Norfolk Naval Station', 'branch': 'navy', 'city': norfolk,
             'description': 'The largest naval base in the world.'},
            {'name': 'Portsmouth Naval Shipyard', 'branch': 'navy', 'city': portsmouth,
             'description': 'Major shipyard for maintaining the U.S. Navy fleet.'},
            {'name': 'Naval Air Station (NAS) Oceana', 'branch': 'navy', 'city': virginia_beach,
             'description': 'Master Jet Base of the U.S. Navy.'},
            {'name': 'JEB Little Creek', 'branch': 'navy', 'city': virginia_beach,
             'description': 'Joint Expeditionary Base Little Creek.'},
            {'name': 'Portsmouth Naval Hospital', 'branch': 'navy', 'city': portsmouth,
             'description': 'Naval medical facility.'},
            # Air Force
            {'name': 'Joint Base Langley-Eustis', 'branch': 'air_force', 'city': hampton,
             'description': 'Air Force led joint base combining Langley AFB and Fort Eustis.'},
            # Coast Guard
            {'name': 'Coast Guard Base Portsmouth', 'branch': 'coast_guard', 'city': portsmouth,
             'description': 'Coast Guard installation.'},
            {'name': 'Coast Guard Training Center Yorktown', 'branch': 'coast_guard', 'city': williamsburg,
             'description': 'Coast Guard training facility.'},
            {'name': 'Coast Guard Atlantic Area (HQ Command)', 'branch': 'coast_guard', 'city': portsmouth,
             'description': 'Headquarters command.'},
            {'name': 'Fifth Coast Guard District (HQ Command)', 'branch': 'coast_guard', 'city': portsmouth,
             'description': 'District headquarters.'},
            {'name': 'Coast Guard Shore Infrastructure Logistics Command (HQ Command)', 'branch': 'coast_guard', 'city': portsmouth,
             'description': 'Logistics headquarters.'},
            # Army
            {'name': 'Fort Eustis', 'branch': 'army', 'city': newport_news,
             'description': 'Part of Joint Base Langley-Eustis.'},
            {'name': 'Fort Story', 'branch': 'army', 'city': virginia_beach,
             'description': 'Part of Joint Expeditionary Base Little Creek - Fort Story.'},
            {'name': 'U.S. Army Corps of Engineers Norfolk District (USACE)', 'branch': 'army', 'city': norfolk,
             'description': 'Army Corps of Engineers district office.'},
            # Marines
            {'name': 'Marine Forces Command (Camp Allen)', 'branch': 'marines', 'city': norfolk,
             'description': 'Marine Corps command facility.'},
            {'name': 'Marine Corps Security Force Regiment', 'branch': 'marines', 'city': williamsburg,
             'description': 'Located at Naval Weapons Station Yorktown.'},
        ]

        for i, base_data in enumerate(bases_data):
            MilitaryBase.objects.create(order=i, **base_data)

        self.stdout.write(f'    Created {MilitaryBase.objects.count()} military bases')

    def seed_tunnels(self):
        self.stdout.write('  Seeding tunnels...')

        tunnels_data = [
            {
                'name': 'Downtown Tunnel',
                'description': 'This tunnel goes through Downtown Norfolk, and connects West Chesapeake (called Western Branch), Suffolk, and Portsmouth to the city of Norfolk.',
                'connects_from': 'Portsmouth/Chesapeake/Suffolk',
                'connects_to': 'Norfolk',
            },
            {
                'name': 'Midtown Tunnel',
                'description': 'Connects West Chesapeake (called Western Branch), Suffolk, and Portsmouth to the city of Norfolk at a midtown location.',
                'connects_from': 'Portsmouth/Chesapeake/Suffolk',
                'connects_to': 'Norfolk (Midtown)',
            },
            {
                'name': 'Hampton Roads Bridge Tunnel (HRBT)',
                'description': 'This tunnel runs along I-64 and is the most common connection between the Hampton Roads Southside & the Peninsula.',
                'connects_from': 'Norfolk/Virginia Beach',
                'connects_to': 'Hampton',
            },
            {
                'name': 'James River Bridge',
                'description': 'To avoid tunnel traffic altogether, this bridge connects western Hampton Roads to the Newport News area of the Peninsula.',
                'connects_from': 'Isle of Wight/Smithfield',
                'connects_to': 'Newport News',
            },
            {
                'name': 'Monitor Merrimac Memorial Bridge/Tunnel',
                'description': 'The MMMBT is less traveled as it is less frequented by military commuters, but a convenient 2nd option for high traffic HRBT days.',
                'connects_from': 'Suffolk/Newport News',
                'connects_to': 'Hampton/Newport News',
            },
            {
                'name': 'Chesapeake Bay Bridge Tunnel',
                'description': 'The Chesapeake Bay Bridge Tunnel connects the southside of Hampton Roads to the state\'s Eastern Shore via Route 13. This route takes you Northeast along the Coast towards Maryland, New Jersey, New York, etc. This is a more rural commute vs. going towards I-95 North, which routes you directly to Northern Virginia and Washington D.C.!',
                'connects_from': 'Virginia Beach',
                'connects_to': 'Eastern Shore',
            },
        ]

        for i, tunnel_data in enumerate(tunnels_data):
            Tunnel.objects.create(order=i, **tunnel_data)

        self.stdout.write(f'    Created {Tunnel.objects.count()} tunnels')

    def seed_vacation_destinations(self):
        self.stdout.write('  Seeding vacation destinations...')

        destinations_data = [
            # Northern Virginia/Maryland (3-5 hours)
            {
                'name': 'Washington D.C.',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': "Our nation's capital!",
            },
            {
                'name': 'Wintergreen or Massanutten',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'Two beautiful Ski Resorts',
            },
            {
                'name': 'Shenandoah National Park',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'Enjoy camping, hiking, & scenery',
            },
            {
                'name': 'Crabtree Falls Campground',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': "This one's a family favorite!",
            },
            {
                'name': 'Luray Caverns',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'The largest caverns on the East Coast',
            },
            {
                'name': 'Charlottesville',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'A historic resort town',
            },
            {
                'name': 'Carter Mountain Orchard',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'Seasonal fruit-picking destination',
            },
            {
                'name': 'Ocean City, MD',
                'distance_description': '3-5 hours (Northern Virginia/Maryland)',
                'highlights': 'Beautiful beaches and casino nightlife',
            },
            # Western Virginia (3-5 hours)
            {
                'name': 'Smith Mountain Lake',
                'distance_description': '3-5 hours (Western Virginia)',
                'highlights': 'Fishing, boating, swimming, etc.!',
            },
            {
                'name': 'Appalachian Trail',
                'distance_description': '3-5 hours (Western Virginia)',
                'highlights': 'The longest hiking-only footpath in the world!',
            },
            {
                'name': "Virginia's Natural Bridge",
                'distance_description': '3-5 hours (Western Virginia)',
                'highlights': 'The largest natural land bridge in North America',
            },
            # Northeast North Carolina (2-6 hours)
            {
                'name': 'Outer Banks',
                'distance_description': '2-6 hours (Northeast North Carolina)',
                'highlights': 'Duck, Nags Head, Hatteras, Manteo, Rodanthe - Where the locals go for beach getaways!',
            },
            {
                'name': 'Biltmore House',
                'distance_description': '2-6 hours (Northeast North Carolina)',
                'highlights': "The Vanderbilt family's home-turned-resort",
            },
        ]

        for i, dest_data in enumerate(destinations_data):
            VacationDestination.objects.create(order=i, **dest_data)

        self.stdout.write(f'    Created {VacationDestination.objects.count()} vacation destinations')

    def seed_vendor_utilities(self):
        self.stdout.write('  Seeding vendor utilities...')

        # Utility data per city
        utilities_by_city = {
            'virginia-beach': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'Virginia Beach Water', 'phone': '(757) 385-4631'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Virginia Beach Trash & Recycling', 'phone': '(757) 385-4650'},
            ],
            'chesapeake': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'gas', 'name': 'Columbia Gas', 'phone': '1-800-543-8911'},
                {'category': 'water', 'name': 'HRSD (Water)', 'phone': '(757) 460-2491'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Chesapeake Trash & Recycling', 'phone': '(757) 382-CITY (2489)'},
            ],
            'norfolk': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'HRSD (Water)', 'phone': '(757) 460-2491'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Norfolk Trash & Recycling', 'phone': '(757) 664-6510'},
            ],
            'portsmouth': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Columbia Gas', 'phone': '1-800-543-8911'},
                {'category': 'water', 'name': 'Portsmouth Water', 'phone': '(757) 393-8524'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Portsmouth Trash & Recycling', 'phone': '(757) 393-8663'},
            ],
            'suffolk': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Columbia Gas', 'phone': '1-800-543-8911'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'HRSD (Water)', 'phone': '(757) 460-2491'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Suffolk Trash & Recycling', 'phone': '(757) 514-7630'},
            ],
            'smithfield': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Columbia Natural Gas', 'phone': '1-800-543-8911'},
                {'category': 'water', 'name': 'Smithfield Water', 'phone': '(757) 365.4200'},
                {'category': 'water', 'name': 'Smithfield Sewage', 'phone': '(757) 365.3338'},
                {'category': 'trash', 'name': 'Smithfield Trash & Recycling', 'phone': '(757) 279.0640'},
            ],
            'hampton': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'Newport News Waterworks', 'phone': '(757) 926-1000'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Hampton Trash & Recycling', 'phone': '(757) 726-2909'},
            ],
            'newport-news': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'Newport News Waterworks', 'phone': '(757) 926-1000'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Newport News Trash & Recycling', 'phone': '(757) 933-2311'},
            ],
            'williamsburg-yorktown': [
                {'category': 'electric', 'name': 'Dominion Utilities', 'phone': '1-866-366-4357'},
                {'category': 'gas', 'name': 'Virginia Natural Gas', 'phone': '1-866-229-3578'},
                {'category': 'water', 'name': 'HRSD (Water)', 'phone': '(757) 460-2491'},
                {'category': 'water', 'name': 'HRSD (Sewage)', 'phone': '(757) 460-2491'},
                {'category': 'trash', 'name': 'Williamsburg Trash & Recycling', 'phone': '(757) 220-6140'},
            ],
        }

        for city_slug, utilities in utilities_by_city.items():
            city = City.objects.get(slug=city_slug)
            for i, utility_data in enumerate(utilities):
                VendorUtility.objects.create(city=city, order=i, **utility_data)

        self.stdout.write(f'    Created {VendorUtility.objects.count()} vendor utilities')

    def seed_testimonials(self):
        self.stdout.write('  Seeding testimonials...')

        testimonials_data = [
            {
                'client_name': 'J Hudson',
                'quote': '''I used the Trustworthy Agents team to help me in the purchase of my home and the experience was amazing. They listened to what I wanted and helped me think about things that would have not been at the forefront of my mind otherwise. They coached me through the process of negotiating and were honest about setting my expectations for what we could and could not ask for. They helped me get a great home and had connections with lenders, inspectors, and even contractors for home improvement ideas. The Trustworthy Agents Group are more than agents, they are an advocate for you and your needs. When I buy my next home, there is no question who I'll be calling on.''',
                'is_featured': True,
            },
            {
                'client_name': 'J. & A. Domino',
                'quote': '''CLOSED!! We did it. We just became co-homeowners. It was a fast (but felt long) ride that took only 22 days from getting pre approved to standing here closing in our new home. We owe it all to the Trustworthy Agents Group. We hit the ground running, and our agent ran with us every step of the way. Something tells me we've made a friend for life. Our Agent fought for us, encouraged us and gave up evenings with his family for us. So here we are toasting to our next venture as homeowners and landlords with the same flutes we drank from on our wedding night. What an awesome house buying experience thanks to Trustworthy Agents Group (who are always welcome at the Domino abode)!''',
                'is_featured': True,
            },
            {
                'client_name': 'B. & J. Graham',
                'quote': '''The Trustworthy Agents Team made what is usually one of the scariest/most stressful times of someone's life a little less stressful. Our agent gave us his honest opinions, he showed us everything we were looking at. He pointed out the pros and cons of homes while walking through. He is definitely in the business to help you find your forever home.''',
                'is_featured': True,
            },
            {
                'client_name': 'A. Parson',
                'quote': '''My husband and I had the best experience working with Nate Pickles to buy our home in 2016. We were having to work long distance from Washington and he bent over backwards to make everything smooth and easy. Then this year we went back to Nate and his dad Robert Pickles to sell our home. They walked through our home and gave me a checklist of things to do to make it show well and hired fantastic photographers. We had 4 great offers in under 24 hours and were under contract the day after our listing went live. Nate and Robert do an amazing job and are available to you anytime you need them. I wish they could always be available to be our agents wherever the Navy takes us!''',
                'is_featured': True,
            },
            {
                'client_name': 'K. Hadley',
                'quote': '''As a first time buyer I was not familiar with the process of buying a home. Nate provided a thorough breakdown of the process and every detail; and if I did have a question I could reach out to him anytime and his response would be immediate. I would recommend Nate and his team to anybody looking to purchase a home in the Tidewater area. Thank you again to Nate; I love my new home.''',
                'is_featured': True,
            },
            {
                'client_name': 'C.F.',
                'quote': '''Robert Pickles has been my trusted Real Estate agent since 2010. Four transactions and several year later, Robert and the Trustworthy Agents have walked me through a site-unseen new build, the purchase and sale of a foreclosure property, and the purchase and rehab of my personal property. I was not experienced with any of these types of transactions, however they took care of the details and gave us wise council every step of the way. Robert even went above and beyond and found me a renter! We were able to transfer from Virginia having sold our last property above market price in less than 2 weeks! Their depth of knowledge and expertise made all the difference, and they come highly recommended.''',
                'is_featured': True,
            },
            {
                'client_name': 'Danielle B.',
                'quote': '''Nate Pickles was by far the best realtor we have ever worked with. He was thorough in explaining everything to us about the whole process and was really good about hearing our concerns. Nate helped us find our dream home quickly which was so important, as time was of the essence with our relocation. He was both professional and prompt on all occasions and was excellent with communicating every step of the way during the entire process. At all times I felt like he was our advocate 100% and it really got our move here to Virginia off to a wonderful start. I would highly recommend him to work with to anyone who is looking for a knowledgeable agent. Thank you so much Nate for getting the job done, we are so excited about our new home and community. You made us feel welcomed!''',
                'is_featured': True,
            },
        ]

        for i, testimonial_data in enumerate(testimonials_data):
            Testimonial.objects.create(order=i, **testimonial_data)

        self.stdout.write(f'    Created {Testimonial.objects.count()} testimonials')

    def seed_team_members(self):
        self.stdout.write('  Seeding team members...')

        team_data = [
            {
                'name': 'Robert Pickles',
                'title': 'CEO & Broker',
                'bio': 'Founder of Trustworthy Agents Group with decades of real estate experience in Hampton Roads.',
                'phone': '757-500-2404',
                'email': 'robert@trustworthyagents.com',
            },
            {
                'name': 'Nate Pickles',
                'title': 'CEO & Realtor',
                'bio': 'Specializing in military relocations and first-time home buyers throughout Hampton Roads.',
                'phone': '757-361-0106',
                'email': 'nate@trustworthyagents.com',
            },
        ]

        for i, member_data in enumerate(team_data):
            TeamMember.objects.create(order=i, **member_data)

        self.stdout.write(f'    Created {TeamMember.objects.count()} team members')
