"""
Content sync utilities for managing dev → prod data migration.

Usage:
    # Export from dev
    python manage.py sync_content --export --type=reference > reference_data.json
    python manage.py sync_content --export --type=cms > cms_content.json

    # Import to prod (after copying json file)
    python manage.py sync_content --import reference_data.json
    python manage.py sync_content --import cms_content.json --preview  # dry run
    python manage.py sync_content --import cms_content.json

Content Types:
    reference - DriveDestination, AIModel, AIProvider, AIOperationConfig, Region
    cms       - City, Venue (base fields only), MilitaryBase, Tunnel,
                VacationDestination, VendorUtility, Testimonial, TeamMember
    api       - Venue enrichment data (ratings, photos, hours) - NOT recommended to sync
"""

import json
import sys
from django.core.management.base import BaseCommand
from django.core import serializers
from guide.models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember,
    DriveDestination
)
from ai_services.models import AIProvider, AIModel, AIOperationConfig


# Fields to EXCLUDE when syncing (API-fetched or auto-generated)
VENUE_EXCLUDE_FIELDS = [
    'google_place_id', 'rating', 'user_ratings_total', 'price_level',
    'formatted_address', 'formatted_phone', 'website', 'latitude', 'longitude',
    'hours_json', 'photos_json', 'last_enriched', 'enrichment_error'
]


class Command(BaseCommand):
    help = 'Export or import content for dev/prod sync'

    def add_arguments(self, parser):
        parser.add_argument('--export', action='store_true', help='Export mode')
        parser.add_argument('--import', dest='import_file', help='Import from JSON file')
        parser.add_argument('--type', choices=['reference', 'cms', 'all'],
                          help='Content type to export')
        parser.add_argument('--preview', action='store_true',
                          help='Preview import without making changes')

    def handle(self, *args, **options):
        if options['export']:
            self.export_content(options['type'])
        elif options['import_file']:
            self.import_content(options['import_file'], options['preview'])
        else:
            self.stderr.write('Use --export or --import <file>')

    def export_content(self, content_type):
        """Export content to JSON (prints to stdout for redirection)."""
        data = {'type': content_type, 'models': {}}

        if content_type in ['reference', 'all']:
            data['models']['Region'] = self._serialize_model(Region)
            data['models']['DriveDestination'] = self._serialize_model(DriveDestination)
            data['models']['AIProvider'] = self._serialize_model(AIProvider)
            data['models']['AIModel'] = self._serialize_model(AIModel)
            data['models']['AIOperationConfig'] = self._serialize_model(AIOperationConfig)

        if content_type in ['cms', 'all']:
            data['models']['City'] = self._serialize_model(City)
            data['models']['Venue'] = self._serialize_model(
                Venue, exclude_fields=VENUE_EXCLUDE_FIELDS
            )
            data['models']['MilitaryBase'] = self._serialize_model(MilitaryBase)
            data['models']['Tunnel'] = self._serialize_model(Tunnel)
            data['models']['VacationDestination'] = self._serialize_model(VacationDestination)
            data['models']['VendorUtility'] = self._serialize_model(VendorUtility)
            data['models']['Testimonial'] = self._serialize_model(Testimonial)
            data['models']['TeamMember'] = self._serialize_model(TeamMember)

        # Output JSON to stdout
        print(json.dumps(data, indent=2, default=str))
        self.stderr.write(self.style.SUCCESS(f'Exported {content_type} content'))

    def _serialize_model(self, model, exclude_fields=None):
        """Serialize a model's data to dict format."""
        records = []
        for obj in model.objects.all():
            record = {}
            for field in obj._meta.fields:
                if exclude_fields and field.name in exclude_fields:
                    continue
                value = getattr(obj, field.name)
                # Handle foreign keys
                if field.is_relation and value is not None:
                    if hasattr(value, 'slug'):
                        record[f'{field.name}_slug'] = value.slug
                    elif hasattr(value, 'pk'):
                        record[f'{field.name}_id'] = value.pk
                else:
                    record[field.name] = value
            records.append(record)
        return records

    def import_content(self, filepath, preview=False):
        """Import content from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File not found: {filepath}'))
            return

        content_type = data.get('type', 'unknown')
        models_data = data.get('models', {})

        self.stdout.write(f"\n{'PREVIEW MODE - ' if preview else ''}Importing {content_type} content\n")
        self.stdout.write('=' * 50)

        # Import order matters for foreign key relationships
        import_order = [
            ('Region', Region, ['slug']),
            ('AIProvider', AIProvider, ['code']),
            ('AIModel', AIModel, ['model_id']),
            ('AIOperationConfig', AIOperationConfig, ['operation_name']),
            ('DriveDestination', DriveDestination, ['slug']),
            ('City', City, ['slug']),
            ('MilitaryBase', MilitaryBase, ['slug']),
            ('Tunnel', Tunnel, ['slug']),
            ('VacationDestination', VacationDestination, ['slug']),
            ('Testimonial', Testimonial, ['client_name']),
            ('TeamMember', TeamMember, ['name']),
            ('VendorUtility', VendorUtility, ['name', 'city_id']),
            ('Venue', Venue, ['slug']),
        ]

        stats = {'created': 0, 'updated': 0, 'skipped': 0}

        for model_name, model_class, lookup_fields in import_order:
            if model_name not in models_data:
                continue

            records = models_data[model_name]
            self.stdout.write(f"\n{model_name}: {len(records)} records")

            for record in records:
                # Build lookup kwargs
                lookup = {}
                for field in lookup_fields:
                    if field in record:
                        lookup[field] = record[field]
                    elif f'{field}_slug' in record:
                        # Resolve foreign key by slug
                        related_model = model_class._meta.get_field(field.replace('_id', '')).related_model
                        try:
                            related_obj = related_model.objects.get(slug=record[f'{field}_slug'])
                            lookup[field.replace('_slug', '')] = related_obj
                        except related_model.DoesNotExist:
                            self.stderr.write(f"  Warning: Related object not found for {field}")
                            continue

                if not lookup:
                    self.stderr.write(f"  Skipping record - no lookup fields")
                    stats['skipped'] += 1
                    continue

                # Prepare defaults (all fields except lookup fields and special fields)
                defaults = {}
                skip_fields = ['id', 'created_at', 'updated_at'] + lookup_fields
                for key, value in record.items():
                    if key in skip_fields or key.endswith('_slug'):
                        continue
                    # Handle foreign keys
                    if key.endswith('_id') and key != 'id':
                        fk_field = key[:-3]  # Remove '_id'
                        if hasattr(model_class, fk_field):
                            try:
                                field_obj = model_class._meta.get_field(fk_field)
                                if field_obj.is_relation:
                                    related_model = field_obj.related_model
                                    if hasattr(related_model, 'slug'):
                                        # Try to find by slug stored elsewhere
                                        pass
                            except:
                                pass
                    defaults[key] = value

                if preview:
                    exists = model_class.objects.filter(**lookup).exists()
                    status = 'UPDATE' if exists else 'CREATE'
                    self.stdout.write(f"  [{status}] {lookup}")
                else:
                    obj, created = model_class.objects.update_or_create(
                        **lookup, defaults=defaults
                    )
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  Created: {obj}")
                    else:
                        stats['updated'] += 1
                        self.stdout.write(f"  Updated: {obj}")

        self.stdout.write('\n' + '=' * 50)
        if preview:
            self.stdout.write(self.style.WARNING('PREVIEW COMPLETE - No changes made'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Import complete: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped"
            ))
