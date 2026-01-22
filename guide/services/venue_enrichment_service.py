"""
Venue Enrichment Service

Orchestration layer for enriching venue data from external APIs.
Handles matching existing venues to API data and discovering new venues.
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Any

from django.db import transaction
from django.utils import timezone

from guide.models import Venue, City, VenueAPIConfig
from .google_places_service import GooglePlacesService

logger = logging.getLogger(__name__)


class VenueEnrichmentService:
    """
    Service for enriching venue data from external APIs.

    Supports:
    - Matching existing manual venues to Google Places
    - Enriching matched venues with ratings, hours, photos
    - Discovering new top-rated venues not in our database
    - Refreshing stale venue data
    """

    # Venue types that can be enriched from APIs
    ENRICHABLE_TYPES = ['restaurant', 'cafe_brewery']

    def __init__(self, provider: str = 'google'):
        """
        Initialize the enrichment service.

        Args:
            provider: API provider to use ('google' or 'yelp')
        """
        self.provider = provider
        self._service = None
        self._config = None

    @property
    def service(self):
        """Lazy-load the provider service."""
        if self._service is None:
            if self.provider == 'google':
                self._service = GooglePlacesService()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        return self._service

    @property
    def config(self) -> Optional[VenueAPIConfig]:
        """Get the API configuration for this provider."""
        if self._config is None:
            self._config = VenueAPIConfig.objects.filter(
                provider=self.provider
            ).first()
        return self._config

    def is_enabled(self) -> bool:
        """Check if the provider is enabled and has quota."""
        if not self.config:
            return False
        return self.config.is_enabled and self.config.has_quota

    def _track_request(self):
        """Track an API request against the quota."""
        if self.config:
            self.config.increment_requests()

    def match_and_enrich_venue(
        self,
        venue: Venue,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Match a single venue to the API and enrich with data.

        Args:
            venue: Venue instance to match and enrich
            dry_run: If True, don't save changes

        Returns:
            Tuple of (success, message)
        """
        if venue.venue_type not in self.ENRICHABLE_TYPES:
            return False, f"Venue type '{venue.venue_type}' not enrichable"

        if not self.is_enabled():
            return False, "API provider not enabled or out of quota"

        # If already has a place ID, just refresh the data
        if venue.google_place_id:
            return self.refresh_venue(venue, dry_run)

        # Try to find a match
        city_name = venue.city.name
        match_data = self.service.find_match(
            name=venue.name,
            address=venue.address,
            city_name=city_name,
            state='VA'
        )
        self._track_request()

        if not match_data:
            if not dry_run:
                venue.enrichment_status = 'manual_review'
                venue.save(update_fields=['enrichment_status'])
            return False, f"No match found for '{venue.name}'"

        # Apply the enrichment data
        if not dry_run:
            self._apply_enrichment(venue, match_data)

        return True, f"Matched '{venue.name}' to Google Place ID: {match_data.get('google_place_id')}"

    def refresh_venue(
        self,
        venue: Venue,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Refresh data for a venue that already has a place ID.

        Args:
            venue: Venue instance with existing place ID
            dry_run: If True, don't save changes

        Returns:
            Tuple of (success, message)
        """
        if not venue.google_place_id:
            return False, "Venue has no Google Place ID"

        if not self.is_enabled():
            return False, "API provider not enabled or out of quota"

        place_data = self.service.get_place_details(venue.google_place_id)
        self._track_request()

        if not place_data:
            if not dry_run:
                venue.enrichment_status = 'failed'
                venue.save(update_fields=['enrichment_status'])
            return False, f"Failed to fetch data for place ID: {venue.google_place_id}"

        if not dry_run:
            self._apply_enrichment(venue, place_data)

        return True, f"Refreshed '{venue.name}'"

    def _apply_enrichment(self, venue: Venue, data: Dict[str, Any]):
        """Apply enrichment data to a venue and save."""
        # Only update fields that have values
        if data.get('google_place_id'):
            venue.google_place_id = data['google_place_id']
        if data.get('address') and not venue.address:
            venue.address = data['address']
        if data.get('phone') and not venue.phone:
            venue.phone = data['phone']
        if data.get('website') and not venue.website:
            venue.website = data['website']
        if data.get('latitude'):
            venue.latitude = data['latitude']
        if data.get('longitude'):
            venue.longitude = data['longitude']
        if data.get('rating') is not None:
            venue.rating = data['rating']
        if data.get('rating_count') is not None:
            venue.rating_count = data['rating_count']
        if data.get('price_level') is not None:
            venue.price_level = data['price_level']
        if data.get('hours_json'):
            venue.hours_json = data['hours_json']
        if data.get('photos_json'):
            venue.photos_json = data['photos_json']

        venue.last_enriched_at = timezone.now()
        venue.enrichment_status = 'success'
        if venue.data_source == 'manual':
            # Keep manual but mark as enriched
            pass
        venue.save()

    def match_and_enrich_city(
        self,
        city: City,
        venue_types: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Match and enrich all venues of specified types in a city.

        Args:
            city: City instance
            venue_types: List of venue types to process (default: ENRICHABLE_TYPES)
            dry_run: If True, don't save changes

        Returns:
            Dictionary with counts of matched, failed, and skipped venues
        """
        if venue_types is None:
            venue_types = self.ENRICHABLE_TYPES

        results = {
            'matched': 0,
            'failed': 0,
            'skipped': 0,
            'details': [],
        }

        venues = Venue.objects.filter(
            city=city,
            venue_type__in=venue_types,
            data_source='manual',
            google_place_id='',  # Not yet matched
        )

        for venue in venues:
            success, message = self.match_and_enrich_venue(venue, dry_run)
            results['details'].append({
                'venue': venue.name,
                'success': success,
                'message': message,
            })

            if success:
                results['matched'] += 1
            else:
                if 'not enrichable' in message:
                    results['skipped'] += 1
                else:
                    results['failed'] += 1

            # Check quota after each request
            if not self.is_enabled():
                logger.warning("Quota exhausted, stopping enrichment")
                break

        return results

    def discover_new_venues(
        self,
        city: City,
        venue_types: Optional[List[str]] = None,
        limit: int = 20,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Discover and add new top-rated venues from the API.

        Args:
            city: City to discover venues for
            venue_types: Types of venues to search (default: ENRICHABLE_TYPES)
            limit: Maximum venues to discover per type
            dry_run: If True, don't create new venues

        Returns:
            Dictionary with counts of added and existing venues
        """
        if venue_types is None:
            venue_types = self.ENRICHABLE_TYPES

        if not self.is_enabled():
            return {'error': 'API provider not enabled or out of quota'}

        results = {
            'added': 0,
            'existing': 0,
            'details': [],
        }

        for venue_type in venue_types:
            # Search for top venues
            search_results = self.service.search_nearby(
                city_name=city.name,
                state='VA',
                venue_type=venue_type,
                limit=limit
            )
            self._track_request()

            for place_data in search_results:
                google_place_id = place_data.get('google_place_id')

                # Check if we already have this venue
                existing = Venue.objects.filter(
                    google_place_id=google_place_id
                ).first()

                if existing:
                    results['existing'] += 1
                    results['details'].append({
                        'name': place_data.get('name'),
                        'action': 'skipped',
                        'reason': 'Already exists',
                    })
                    continue

                # Check by name similarity
                name = place_data.get('name', '')
                name_match = Venue.objects.filter(
                    city=city,
                    name__iexact=name,
                    venue_type=venue_type
                ).first()

                if name_match:
                    # Update existing with API data
                    if not dry_run:
                        self._apply_enrichment(name_match, place_data)
                    results['existing'] += 1
                    results['details'].append({
                        'name': name,
                        'action': 'matched',
                        'reason': 'Matched by name',
                    })
                    continue

                # Create new venue
                if not dry_run:
                    venue = Venue.objects.create(
                        city=city,
                        venue_type=venue_type,
                        name=name,
                        address=place_data.get('address', ''),
                        phone=place_data.get('phone', ''),
                        website=place_data.get('website', ''),
                        latitude=place_data.get('latitude'),
                        longitude=place_data.get('longitude'),
                        google_place_id=google_place_id,
                        rating=place_data.get('rating'),
                        rating_count=place_data.get('rating_count'),
                        price_level=place_data.get('price_level'),
                        hours_json=place_data.get('hours_json'),
                        photos_json=place_data.get('photos_json'),
                        data_source='google',
                        last_enriched_at=timezone.now(),
                        enrichment_status='success',
                        is_published=True,
                    )

                results['added'] += 1
                results['details'].append({
                    'name': name,
                    'action': 'added',
                    'rating': place_data.get('rating'),
                })

            if not self.is_enabled():
                logger.warning("Quota exhausted, stopping discovery")
                break

        return results

    def refresh_stale_venues(
        self,
        days_old: int = 7,
        limit: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Refresh venues that haven't been updated in N days.

        Args:
            days_old: Refresh venues older than this many days
            limit: Maximum number of venues to refresh
            dry_run: If True, don't save changes

        Returns:
            Dictionary with refresh results
        """
        cutoff_date = timezone.now() - timedelta(days=days_old)

        # Find stale venues with Google Place IDs
        stale_venues = Venue.objects.filter(
            google_place_id__isnull=False,
            venue_type__in=self.ENRICHABLE_TYPES,
        ).exclude(
            google_place_id=''
        ).filter(
            last_enriched_at__lt=cutoff_date
        ).order_by('last_enriched_at')

        if limit:
            stale_venues = stale_venues[:limit]

        results = {
            'refreshed': 0,
            'failed': 0,
            'details': [],
        }

        for venue in stale_venues:
            success, message = self.refresh_venue(venue, dry_run)
            results['details'].append({
                'venue': venue.name,
                'success': success,
                'message': message,
            })

            if success:
                results['refreshed'] += 1
            else:
                results['failed'] += 1

            if not self.is_enabled():
                logger.warning("Quota exhausted, stopping refresh")
                break

        return results

    def get_enrichment_stats(self) -> Dict[str, Any]:
        """
        Get statistics about venue enrichment status.

        Returns:
            Dictionary with enrichment statistics
        """
        from django.db.models import Count

        total = Venue.objects.filter(venue_type__in=self.ENRICHABLE_TYPES).count()
        enriched = Venue.objects.filter(
            venue_type__in=self.ENRICHABLE_TYPES,
            enrichment_status='success'
        ).count()
        pending = Venue.objects.filter(
            venue_type__in=self.ENRICHABLE_TYPES,
            enrichment_status='none'
        ).count()
        manual_review = Venue.objects.filter(
            venue_type__in=self.ENRICHABLE_TYPES,
            enrichment_status='manual_review'
        ).count()

        by_source = Venue.objects.filter(
            venue_type__in=self.ENRICHABLE_TYPES
        ).values('data_source').annotate(count=Count('id'))

        return {
            'total': total,
            'enriched': enriched,
            'pending': pending,
            'manual_review': manual_review,
            'enrichment_rate': round((enriched / total * 100) if total else 0, 1),
            'by_source': {item['data_source']: item['count'] for item in by_source},
            'quota_remaining': self.config.quota_remaining if self.config else 0,
            'last_sync': self.config.last_full_sync if self.config else None,
        }
