"""
Yelp Fusion Service (Stub)

Placeholder for future Yelp Fusion API integration.
"""

import logging
from typing import Dict, List, Optional, Any

from .base_venue_service import BaseVenueService

logger = logging.getLogger(__name__)


class YelpService(BaseVenueService):
    """
    Service for interacting with Yelp Fusion API.

    This is a stub implementation for future development.
    Yelp provides complementary data to Google Places:
    - More detailed reviews
    - Different rating scale
    - Additional business categories
    """

    # Map our venue types to Yelp categories
    # See: https://www.yelp.com/developers/documentation/v3/all_category_list
    VENUE_TYPE_MAP = {
        'restaurant': ['restaurants'],
        'cafe_brewery': ['coffee', 'breweries', 'bars'],
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Yelp service.

        Args:
            api_key: Yelp Fusion API key
        """
        self.api_key = api_key
        logger.info("Yelp service initialized (stub - not yet implemented)")

    @property
    def provider_name(self) -> str:
        return 'yelp'

    def search_nearby(
        self,
        city_name: str,
        state: str = 'VA',
        venue_type: str = 'restaurant',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for venues near a city.

        Not yet implemented - returns empty list.
        """
        logger.warning("Yelp search_nearby not implemented")
        return []

    def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a Yelp business.

        Not yet implemented - returns None.
        """
        logger.warning("Yelp get_place_details not implemented")
        return None

    def find_match(
        self,
        name: str,
        address: str,
        city_name: str,
        state: str = 'VA'
    ) -> Optional[Dict[str, Any]]:
        """
        Find a matching Yelp business for an existing venue.

        Not yet implemented - returns None.
        """
        logger.warning("Yelp find_match not implemented")
        return None

    def normalize_venue_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Yelp data to our Venue model format.

        Placeholder for future implementation.
        """
        return {
            'yelp_business_id': raw_data.get('id', ''),
            'name': raw_data.get('name', ''),
            'address': '',
            'phone': raw_data.get('phone', ''),
            'website': raw_data.get('url', ''),
            'latitude': None,
            'longitude': None,
            'rating': raw_data.get('rating'),
            'rating_count': raw_data.get('review_count'),
            'price_level': len(raw_data.get('price', '')) if raw_data.get('price') else None,
            'hours_json': None,
            'photos_json': None,
        }
