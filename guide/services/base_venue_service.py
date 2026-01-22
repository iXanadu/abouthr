"""
Base Venue Service

Abstract base class for venue data provider services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseVenueService(ABC):
    """
    Abstract base class for external venue data providers.

    Subclasses must implement methods for searching venues and
    fetching detailed place information.
    """

    # Mapping of our venue types to provider-specific types
    VENUE_TYPE_MAP: Dict[str, List[str]] = {}

    @abstractmethod
    def search_nearby(
        self,
        city_name: str,
        state: str,
        venue_type: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for venues near a city.

        Args:
            city_name: Name of the city to search
            state: State abbreviation (e.g., 'VA')
            venue_type: Our internal venue type (restaurant, cafe_brewery, etc.)
            limit: Maximum number of results to return

        Returns:
            List of venue data dictionaries
        """
        pass

    @abstractmethod
    def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific place.

        Args:
            place_id: Provider's unique place identifier
            fields: Optional list of specific fields to retrieve

        Returns:
            Dictionary of place details or None if not found
        """
        pass

    @abstractmethod
    def find_match(
        self,
        name: str,
        address: str,
        city_name: str,
        state: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a matching place for an existing venue.

        Args:
            name: Venue name to search for
            address: Venue address
            city_name: City name
            state: State abbreviation

        Returns:
            Matching place data or None if no match found
        """
        pass

    def normalize_venue_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific data to our standard format.

        Override in subclasses to handle provider-specific fields.

        Args:
            raw_data: Raw data from the provider

        Returns:
            Normalized data dictionary matching Venue model fields
        """
        return raw_data

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g., 'google', 'yelp')."""
        pass
