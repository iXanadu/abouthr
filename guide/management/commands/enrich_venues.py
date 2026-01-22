"""
Management Command: enrich_venues

Match and enrich existing venues with data from external APIs,
and optionally discover new top-rated venues.

Usage:
    # Match & enrich existing restaurants in all cities
    python manage.py enrich_venues --type=restaurant

    # Enrich + discover new top venues for Norfolk
    python manage.py enrich_venues --city=norfolk --discover --limit=20

    # Enrich all enrichable types
    python manage.py enrich_venues --all

    # Dry run - show what would be matched/added
    python manage.py enrich_venues --dry-run

    # Flag unmatched venues for manual review
    python manage.py enrich_venues --flag-unmatched
"""

from django.core.management.base import BaseCommand, CommandError

from guide.models import City, Venue, VenueAPIConfig
from guide.services import VenueEnrichmentService


class Command(BaseCommand):
    help = 'Enrich venues with data from external APIs (Google Places, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            help='City slug to process (default: all cities)',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['restaurant', 'cafe_brewery'],
            help='Venue type to process',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all enrichable venue types',
        )
        parser.add_argument(
            '--discover',
            action='store_true',
            help='Also discover new top-rated venues not in our database',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum venues to discover per city/type (default: 20)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--flag-unmatched',
            action='store_true',
            help='Flag unmatched venues for manual review',
        )
        parser.add_argument(
            '--provider',
            type=str,
            default='google',
            choices=['google'],
            help='API provider to use (default: google)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        discover = options['discover']
        limit = options['limit']
        provider = options['provider']

        # Determine venue types to process
        if options['all']:
            venue_types = VenueEnrichmentService.ENRICHABLE_TYPES
        elif options['type']:
            venue_types = [options['type']]
        else:
            venue_types = VenueEnrichmentService.ENRICHABLE_TYPES

        # Determine cities to process
        if options['city']:
            cities = City.objects.filter(slug=options['city'])
            if not cities.exists():
                raise CommandError(f"City not found: {options['city']}")
        else:
            cities = City.objects.filter(is_published=True)

        # Check API configuration
        config = VenueAPIConfig.objects.filter(provider=provider).first()
        if not config:
            self.stdout.write(self.style.WARNING(
                f"No {provider} API configuration found. Creating default..."
            ))
            config = VenueAPIConfig.objects.create(
                provider=provider,
                api_key_name='GOOGLE_PLACES_API_KEY',
            )

        if not config.is_enabled:
            self.stdout.write(self.style.WARNING(
                f"API provider '{provider}' is not enabled. "
                "Enable it in CMS settings or update VenueAPIConfig."
            ))
            if not dry_run:
                return

        # Initialize service
        service = VenueEnrichmentService(provider=provider)

        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes will be made"))

        self.stdout.write(f"\nProcessing {cities.count()} cities...")
        self.stdout.write(f"Venue types: {', '.join(venue_types)}")
        self.stdout.write(f"Quota remaining: {config.quota_remaining}")
        self.stdout.write("")

        total_matched = 0
        total_failed = 0
        total_added = 0

        for city in cities:
            self.stdout.write(f"\n{'=' * 50}")
            self.stdout.write(self.style.HTTP_INFO(f"Processing: {city.name}"))
            self.stdout.write(f"{'=' * 50}")

            # Match and enrich existing venues
            self.stdout.write("\nMatching existing venues...")
            results = service.match_and_enrich_city(
                city=city,
                venue_types=venue_types,
                dry_run=dry_run
            )

            total_matched += results['matched']
            total_failed += results['failed']

            for detail in results['details']:
                if detail['success']:
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ {detail['venue']}: {detail['message']}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"  ✗ {detail['venue']}: {detail['message']}"
                    ))

            self.stdout.write(
                f"\n  Matched: {results['matched']}, "
                f"Failed: {results['failed']}, "
                f"Skipped: {results['skipped']}"
            )

            # Discover new venues if requested
            if discover:
                self.stdout.write("\nDiscovering new venues...")
                discover_results = service.discover_new_venues(
                    city=city,
                    venue_types=venue_types,
                    limit=limit,
                    dry_run=dry_run
                )

                if 'error' in discover_results:
                    self.stdout.write(self.style.ERROR(
                        f"  Error: {discover_results['error']}"
                    ))
                else:
                    total_added += discover_results['added']

                    for detail in discover_results['details']:
                        if detail['action'] == 'added':
                            rating = detail.get('rating', 'N/A')
                            self.stdout.write(self.style.SUCCESS(
                                f"  + {detail['name']} (rating: {rating})"
                            ))
                        elif detail['action'] == 'matched':
                            self.stdout.write(self.style.HTTP_INFO(
                                f"  ~ {detail['name']}: {detail['reason']}"
                            ))

                    self.stdout.write(
                        f"\n  Added: {discover_results['added']}, "
                        f"Existing: {discover_results['existing']}"
                    )

            # Check quota
            if not service.is_enabled():
                self.stdout.write(self.style.ERROR(
                    "\nQuota exhausted! Stopping."
                ))
                break

        # Summary
        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(self.style.HTTP_INFO("SUMMARY"))
        self.stdout.write(f"{'=' * 50}")
        self.stdout.write(f"Total matched: {total_matched}")
        self.stdout.write(f"Total failed: {total_failed}")
        if discover:
            self.stdout.write(f"Total added: {total_added}")
        self.stdout.write(f"Quota remaining: {service.config.quota_remaining if service.config else 'N/A'}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("\nDRY RUN - No changes were made"))

        # Flag unmatched venues if requested
        if options['flag_unmatched'] and not dry_run:
            unmatched = Venue.objects.filter(
                venue_type__in=venue_types,
                google_place_id='',
                enrichment_status='none'
            ).update(enrichment_status='manual_review')
            self.stdout.write(f"\nFlagged {unmatched} venues for manual review")
