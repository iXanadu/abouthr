"""
Management Command: refresh_venues

Refresh stale venue data from external APIs.

Usage:
    # Refresh venues not updated in 7+ days
    python manage.py refresh_venues --days=7

    # Refresh specific venue by ID
    python manage.py refresh_venues --venue-id=123

    # Refresh all enriched venues
    python manage.py refresh_venues --all

    # Limit number of venues to refresh
    python manage.py refresh_venues --days=7 --limit=50

    # Dry run
    python manage.py refresh_venues --days=7 --dry-run
"""

from django.core.management.base import BaseCommand, CommandError

from guide.models import Venue, VenueAPIConfig
from guide.services import VenueEnrichmentService


class Command(BaseCommand):
    help = 'Refresh stale venue data from external APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Refresh venues not updated in N days (default: 7)',
        )
        parser.add_argument(
            '--venue-id',
            type=int,
            help='Refresh a specific venue by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Refresh all enriched venues regardless of age',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of venues to refresh',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
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
        provider = options['provider']
        days = options['days']
        limit = options['limit']

        # Check API configuration
        config = VenueAPIConfig.objects.filter(provider=provider).first()
        if not config or not config.is_enabled:
            self.stdout.write(self.style.ERROR(
                f"API provider '{provider}' is not configured or enabled."
            ))
            return

        service = VenueEnrichmentService(provider=provider)

        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes will be made"))

        self.stdout.write(f"Quota remaining: {config.quota_remaining}")
        self.stdout.write("")

        # Refresh specific venue
        if options['venue_id']:
            try:
                venue = Venue.objects.get(pk=options['venue_id'])
            except Venue.DoesNotExist:
                raise CommandError(f"Venue not found: {options['venue_id']}")

            if not venue.google_place_id:
                self.stdout.write(self.style.WARNING(
                    f"Venue '{venue.name}' has no Google Place ID. "
                    "Use enrich_venues to match it first."
                ))
                return

            self.stdout.write(f"Refreshing venue: {venue.name}")
            success, message = service.refresh_venue(venue, dry_run)

            if success:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"  ✗ {message}"))
            return

        # Refresh all enriched venues (use very old cutoff)
        if options['all']:
            days = 36500  # ~100 years, effectively all venues

        # Refresh stale venues
        self.stdout.write(f"Finding venues not updated in {days}+ days...")

        results = service.refresh_stale_venues(
            days_old=days,
            limit=limit,
            dry_run=dry_run
        )

        total = len(results['details'])
        self.stdout.write(f"Found {total} venues to refresh\n")

        for detail in results['details']:
            if detail['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ {detail['venue']}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"  ✗ {detail['venue']}: {detail['message']}"
                ))

        # Summary
        self.stdout.write(f"\n{'=' * 40}")
        self.stdout.write(f"Refreshed: {results['refreshed']}")
        self.stdout.write(f"Failed: {results['failed']}")
        self.stdout.write(f"Quota remaining: {service.config.quota_remaining if service.config else 'N/A'}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("\nDRY RUN - No changes were made"))
