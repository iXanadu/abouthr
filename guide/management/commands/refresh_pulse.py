"""
Management command to refresh Hampton Roads Pulse content.

Usage:
    python manage.py refresh_pulse           # Refresh expired content only
    python manage.py refresh_pulse --force   # Force refresh all
    python manage.py refresh_pulse --trends  # Refresh trends only
    python manage.py refresh_pulse --headlines  # Refresh headlines only
    python manage.py refresh_pulse --stats   # Show pulse statistics
"""
from django.core.management.base import BaseCommand
from guide.services.pulse_service import pulse_service


class Command(BaseCommand):
    help = 'Refresh Hampton Roads Pulse content (trends and headlines)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh even if cache is valid'
        )
        parser.add_argument(
            '--trends',
            action='store_true',
            help='Refresh only trends'
        )
        parser.add_argument(
            '--headlines',
            action='store_true',
            help='Refresh only headlines'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show pulse statistics'
        )

    def handle(self, *args, **options):
        if options['stats']:
            stats = pulse_service.get_stats()
            self.stdout.write("\n=== Hampton Roads Pulse Statistics ===\n")

            self.stdout.write(f"Trends:")
            if stats['trends_active']:
                self.stdout.write(f"  Status: ACTIVE")
                self.stdout.write(f"  Updated: {stats['trends_updated']}")
                self.stdout.write(f"  Expires: {stats['trends_expires']}")
            else:
                self.stdout.write(f"  Status: EXPIRED/EMPTY")

            self.stdout.write(f"\nHeadlines:")
            if stats['headlines_active']:
                self.stdout.write(f"  Status: ACTIVE")
                self.stdout.write(f"  Updated: {stats['headlines_updated']}")
                self.stdout.write(f"  Expires: {stats['headlines_expires']}")
            else:
                self.stdout.write(f"  Status: EXPIRED/EMPTY")

            self.stdout.write(f"\nThis Month:")
            self.stdout.write(f"  Total Cost: ${stats['month_cost']:.4f}")
            self.stdout.write(f"  Refreshes: {stats['month_refreshes']}")
            self.stdout.write(f"  Tokens Used: {stats['month_tokens']:,}")
            return

        if options['force']:
            self.stdout.write("Force refreshing pulse content...")

            if options['trends']:
                result = pulse_service.force_refresh('trends')
            elif options['headlines']:
                result = pulse_service.force_refresh('headlines')
            else:
                result = pulse_service.force_refresh()

            for content_type, status in result.items():
                if status == 'success':
                    self.stdout.write(self.style.SUCCESS(f"  {content_type}: {status}"))
                else:
                    self.stdout.write(self.style.ERROR(f"  {content_type}: {status}"))
        else:
            # Normal refresh (only if expired)
            self.stdout.write("Checking pulse content (will refresh if expired)...")
            data = pulse_service.get_pulse_data(refresh_if_expired=True)

            trends_count = len(data['trends'].get('items', []))
            headlines_count = len(data['headlines'].get('items', []))

            if trends_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"  Trends: {trends_count} items (updated: {data['trends_updated']})"
                ))
            else:
                self.stdout.write(self.style.WARNING("  Trends: EMPTY"))

            if headlines_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"  Headlines: {headlines_count} items (updated: {data['headlines_updated']})"
                ))
            else:
                self.stdout.write(self.style.WARNING("  Headlines: EMPTY"))
