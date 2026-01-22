"""
Google Places Service

Client for Google Places API (New) to fetch venue data.
Uses field masks to control costs per the API pricing tiers.
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from django.conf import settings

from .base_venue_service import BaseVenueService

logger = logging.getLogger(__name__)


class GooglePlacesService(BaseVenueService):
    """
    Service for interacting with Google Places API (New).

    Uses the Places API (New) with field masks to minimize costs:
    - Basic tier: name, address, phone, website, location
    - Advanced tier: rating, reviews, price_level, hours, photos
    """

    BASE_URL = "https://places.googleapis.com/v1"

    # Map our venue types to Google place types
    # See: https://developers.google.com/maps/documentation/places/web-service/place-types
    VENUE_TYPE_MAP = {
        'restaurant': ['restaurant', 'meal_takeaway', 'meal_delivery'],
        'cafe_brewery': ['cafe', 'bar', 'bakery'],
    }

    # Fields by pricing tier
    BASIC_FIELDS = [
        'places.id',
        'places.displayName',
        'places.formattedAddress',
        'places.nationalPhoneNumber',
        'places.websiteUri',
        'places.location',
        'places.googleMapsUri',
    ]

    ADVANCED_FIELDS = [
        'places.rating',
        'places.userRatingCount',
        'places.priceLevel',
        'places.currentOpeningHours',
        'places.regularOpeningHours',
        'places.photos',
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Places service.

        Args:
            api_key: Google Places API key. If not provided, reads from settings.
        """
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            logger.warning("Google Places API key not configured")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings or environment."""
        # Try to get from VenueAPIConfig model first
        try:
            from guide.models import VenueAPIConfig
            config = VenueAPIConfig.objects.filter(
                provider='google',
                is_enabled=True
            ).first()
            if config:
                import os
                key_name = config.api_key_name
                return os.environ.get(key_name) or getattr(settings, key_name, None)
        except Exception:
            pass

        # Fall back to direct settings
        return getattr(settings, 'GOOGLE_PLACES_API_KEY', None)

    @property
    def provider_name(self) -> str:
        return 'google'

    def _make_request(
        self,
        endpoint: str,
        method: str = 'POST',
        data: Optional[Dict] = None,
        field_mask: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Google Places API.

        Args:
            endpoint: API endpoint path
            method: HTTP method (POST, GET)
            data: Request body data
            field_mask: Fields to include in response

        Returns:
            Response JSON or None on error
        """
        if not self.api_key:
            logger.error("Google Places API key not configured")
            return None

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
        }

        if field_mask:
            headers['X-Goog-FieldMask'] = ','.join(field_mask)

        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places API error: {e}")
            return None

    def search_nearby(
        self,
        city_name: str,
        state: str = 'VA',
        venue_type: str = 'restaurant',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for top-rated venues near a city using Text Search.

        Uses Text Search (New) to find venues by type in a city,
        sorted by relevance/prominence.
        """
        google_types = self.VENUE_TYPE_MAP.get(venue_type, ['restaurant'])

        all_results = []
        for place_type in google_types:
            query = f"best {place_type}s in {city_name}, {state}"

            data = {
                'textQuery': query,
                'includedType': place_type,
                'maxResultCount': min(limit, 20),  # API max is 20 per request
                'rankPreference': 'RELEVANCE',
            }

            # Use both basic and advanced fields for search results
            field_mask = self.BASIC_FIELDS + self.ADVANCED_FIELDS

            result = self._make_request(
                'places:searchText',
                method='POST',
                data=data,
                field_mask=field_mask
            )

            if result and 'places' in result:
                for place in result['places']:
                    normalized = self.normalize_venue_data(place)
                    normalized['_search_type'] = place_type
                    all_results.append(normalized)

            if len(all_results) >= limit:
                break

        # Sort by rating (descending) and return top N
        all_results.sort(key=lambda x: (x.get('rating') or 0), reverse=True)
        return all_results[:limit]

    def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific place.

        Args:
            place_id: Google Place ID (format: places/XXXXX)
            fields: Optional specific fields to retrieve

        Returns:
            Normalized place data or None
        """
        # Ensure place_id has proper prefix
        if not place_id.startswith('places/'):
            place_id = f'places/{place_id}'

        if fields is None:
            # Request all relevant fields
            field_mask = [f.replace('places.', '') for f in
                         self.BASIC_FIELDS + self.ADVANCED_FIELDS]
        else:
            field_mask = fields

        # Format field mask for single place (not search)
        formatted_mask = [f for f in field_mask]

        result = self._make_request(
            place_id,
            method='GET',
            field_mask=formatted_mask
        )

        if result:
            return self.normalize_venue_data(result)
        return None

    def find_match(
        self,
        name: str,
        address: str,
        city_name: str,
        state: str = 'VA'
    ) -> Optional[Dict[str, Any]]:
        """
        Find a matching Google Place for an existing venue.

        Uses Text Search with the venue name and city to find matches.
        """
        # Build search query with name and location
        query = f"{name} {city_name}, {state}"
        if address:
            query = f"{name} {address}"

        data = {
            'textQuery': query,
            'maxResultCount': 5,
        }

        field_mask = self.BASIC_FIELDS + self.ADVANCED_FIELDS

        result = self._make_request(
            'places:searchText',
            method='POST',
            data=data,
            field_mask=field_mask
        )

        if not result or 'places' not in result:
            return None

        # Find best match by comparing names
        places = result['places']
        name_lower = name.lower()

        for place in places:
            place_name = place.get('displayName', {}).get('text', '').lower()
            # Check for name similarity
            if name_lower in place_name or place_name in name_lower:
                return self.normalize_venue_data(place)

        # If no exact match, return first result if it's in the right city
        if places:
            first = places[0]
            address_str = first.get('formattedAddress', '').lower()
            if city_name.lower() in address_str:
                return self.normalize_venue_data(first)

        return None

    def normalize_venue_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Google Places data to our Venue model format.
        """
        # Extract place ID
        place_id = raw_data.get('id', '') or raw_data.get('name', '')
        if place_id.startswith('places/'):
            place_id = place_id[7:]  # Remove 'places/' prefix

        # Extract display name
        display_name = raw_data.get('displayName', {})
        name = display_name.get('text', '') if isinstance(display_name, dict) else str(display_name)

        # Extract location
        location = raw_data.get('location', {})
        lat = location.get('latitude')
        lng = location.get('longitude')

        # Extract hours
        hours_data = raw_data.get('regularOpeningHours') or raw_data.get('currentOpeningHours')
        hours_json = None
        if hours_data:
            hours_json = {
                'weekdayDescriptions': hours_data.get('weekdayDescriptions', []),
                'periods': hours_data.get('periods', []),
            }

        # Extract photos (store references for later fetching)
        photos = raw_data.get('photos', [])
        photos_json = None
        if photos:
            photos_json = [
                {
                    'name': p.get('name'),
                    'widthPx': p.get('widthPx'),
                    'heightPx': p.get('heightPx'),
                }
                for p in photos[:5]  # Limit to 5 photos
            ]

        # Map price level
        price_level_map = {
            'PRICE_LEVEL_FREE': 0,
            'PRICE_LEVEL_INEXPENSIVE': 1,
            'PRICE_LEVEL_MODERATE': 2,
            'PRICE_LEVEL_EXPENSIVE': 3,
            'PRICE_LEVEL_VERY_EXPENSIVE': 4,
        }
        price_level = price_level_map.get(raw_data.get('priceLevel'))

        return {
            'google_place_id': place_id,
            'name': name,
            'address': raw_data.get('formattedAddress', ''),
            'phone': raw_data.get('nationalPhoneNumber', ''),
            'website': raw_data.get('websiteUri', ''),
            'latitude': lat,
            'longitude': lng,
            'rating': raw_data.get('rating'),
            'rating_count': raw_data.get('userRatingCount'),
            'price_level': price_level,
            'hours_json': hours_json,
            'photos_json': photos_json,
            'google_maps_url': raw_data.get('googleMapsUri', ''),
        }

    def get_photo_url(self, photo_name: str, max_width: int = 400) -> str:
        """
        Get a URL for a photo reference.

        Note: Requires additional API call to fetch photo.
        """
        if not photo_name or not self.api_key:
            return ''

        return (
            f"{self.BASE_URL}/{photo_name}/media"
            f"?maxWidthPx={max_width}&key={self.api_key}"
        )
