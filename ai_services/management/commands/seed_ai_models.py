"""
Seed AI providers and models from providers.yaml

Usage:
    python manage.py seed_ai_models           # Seed all providers, models, and configs
    python manage.py seed_ai_models --dry-run # Show what would be created without changes
    python manage.py seed_ai_models --reset   # Delete existing data before seeding
"""

from django.core.management.base import BaseCommand
from ai_services.models import AIProvider, AIModel, AIOperationConfig
from ai_services.pricing import get_all_pricing
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed AI providers, models, and default operation configs from providers.yaml'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before seeding (use with caution)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reset = options['reset']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        if reset and not dry_run:
            self.stdout.write(self.style.WARNING('Resetting existing data...\n'))
            AIOperationConfig.objects.all().delete()
            AIModel.objects.all().delete()
            AIProvider.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data deleted.\n'))

        # Seed providers
        providers = self._seed_providers(dry_run)

        # Seed models from providers.yaml pricing data
        self._seed_models(providers, dry_run)

        # Seed default operation configs
        self._seed_operation_configs(providers, dry_run)

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))

    def _seed_providers(self, dry_run: bool) -> dict:
        """Create AI providers and return mapping"""
        self.stdout.write('\n=== Seeding AI Providers ===\n')

        providers_data = [
            ('openai', 'OpenAI', 'openai', 'OPENAI_API_KEY'),
            ('anthropic', 'Anthropic', 'anthropic', 'ANTHROPIC_API_KEY'),
            ('xai', 'xAI', 'xai', 'XAI_API_KEY'),
            ('blackforestlabs', 'Black Forest Labs', 'blackforestlabs', 'BFL_API_KEY'),
            ('google', 'Google (Gemini)', 'google', 'GOOGLE_AI_API_KEY'),
        ]

        providers = {}
        for name, display, ptype, env_var in providers_data:
            if dry_run:
                self.stdout.write(f"  Would create provider: {display} ({name})")
                providers[name] = None
            else:
                provider, created = AIProvider.objects.update_or_create(
                    name=name,
                    defaults={
                        'display_name': display,
                        'provider_type': ptype,
                        'api_key_env_var': env_var,
                    }
                )
                providers[name] = provider
                status = 'Created' if created else 'Updated'
                self.stdout.write(f"  {status}: {display}")

        return providers

    def _seed_models(self, providers: dict, dry_run: bool):
        """Create AI models from providers.yaml pricing data"""
        self.stdout.write('\n=== Seeding AI Models ===\n')

        # Get pricing from providers.yaml
        pricing = get_all_pricing()

        # Define capabilities for known models
        model_capabilities = {
            # OpenAI
            'gpt-4o': ['text', 'vision', 'code'],
            'gpt-4o-mini': ['text', 'vision', 'code'],
            'gpt-4-turbo': ['text', 'vision', 'code'],
            # Anthropic Claude 4.x
            'claude-opus-4-5-20251101': ['text', 'vision', 'code'],
            'claude-sonnet-4-5-20251022': ['text', 'vision', 'code'],
            'claude-haiku-4-5-20251001': ['text', 'vision', 'code'],
            'claude-sonnet-4-20250514': ['text', 'vision', 'code'],
            # Anthropic Claude 3.x
            'claude-3-5-sonnet-20241022': ['text', 'vision', 'code'],
            'claude-3-haiku-20240307': ['text', 'vision', 'code'],
            # xAI Grok 4.x (with web search and reasoning)
            'grok-4-1-fast-reasoning': ['text', 'code', 'web_search'],
            'grok-4': ['text', 'code', 'web_search'],
            # xAI Grok 3.x
            'grok-3': ['text', 'code', 'web_search'],
            'grok-3-fast': ['text', 'code', 'web_search'],
            # Black Forest Labs FLUX
            'flux-2-pro': ['image_gen'],
            'flux-2-flex': ['image_gen'],
            # Google Gemini
            'gemini-2.0-flash': ['text', 'vision', 'code'],
        }

        # Define display names for models
        display_names = {
            # OpenAI
            'gpt-4o': 'GPT-4o',
            'gpt-4o-mini': 'GPT-4o Mini',
            'gpt-4-turbo': 'GPT-4 Turbo',
            # Anthropic
            'claude-opus-4-5-20251101': 'Claude Opus 4.5',
            'claude-sonnet-4-5-20251022': 'Claude Sonnet 4.5',
            'claude-haiku-4-5-20251001': 'Claude Haiku 4.5',
            'claude-sonnet-4-20250514': 'Claude Sonnet 4',
            'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
            'claude-3-haiku-20240307': 'Claude 3 Haiku',
            # xAI Grok 4.x
            'grok-4-1-fast-reasoning': 'Grok 4.1 Fast Reasoning',
            'grok-4': 'Grok 4',
            # xAI Grok 3.x
            'grok-3': 'Grok 3',
            'grok-3-fast': 'Grok 3 Fast',
            # FLUX
            'flux-2-pro': 'FLUX 2 Pro',
            'flux-2-flex': 'FLUX 2 Flex',
            # Google
            'gemini-2.0-flash': 'Gemini 2.0 Flash',
        }

        for provider_name, models in pricing.items():
            if provider_name == 'default':
                continue
            if provider_name not in providers:
                continue

            provider = providers[provider_name]
            self.stdout.write(f"\n  {provider_name}:")

            for model_id, rates in models.items():
                capabilities = model_capabilities.get(model_id, ['text'])
                display_name = display_names.get(model_id, model_id)

                # Extract pricing
                input_price = rates.get('input')
                output_price = rates.get('output')
                per_image = rates.get('per_image')

                if dry_run:
                    self.stdout.write(f"    Would create: {display_name} ({model_id})")
                else:
                    model, created = AIModel.objects.update_or_create(
                        provider=provider,
                        model_id=model_id,
                        defaults={
                            'display_name': display_name,
                            'capabilities': capabilities,
                            'input_price_per_1k': Decimal(str(input_price)) if input_price else None,
                            'output_price_per_1k': Decimal(str(output_price)) if output_price else None,
                            'price_per_image': Decimal(str(per_image)) if per_image else None,
                        }
                    )
                    status = 'Created' if created else 'Updated'
                    self.stdout.write(f"    {status}: {display_name}")

    def _seed_operation_configs(self, providers: dict, dry_run: bool):
        """Create default operation configurations"""
        self.stdout.write('\n=== Seeding Default Operation Configs ===\n')

        # Default configs - matches HARDCODED_DEFAULTS in model_selector.py
        default_configs = [
            # (operation, provider_name, model_id, temperature, max_tokens)
            # Content Generation - Claude Haiku (cheap, fast)
            ('content_venue_description', 'anthropic', 'claude-haiku-4-5-20251001', 0.7, 500),
            ('content_city_description', 'anthropic', 'claude-haiku-4-5-20251001', 0.7, 800),
            ('content_refresh', 'anthropic', 'claude-haiku-4-5-20251001', 0.3, 500),
            # Web Research - Grok 4 (web search capability)
            ('research_events', 'xai', 'grok-4-1-fast-reasoning', 0.5, 2000),
            ('research_happenings', 'xai', 'grok-4-1-fast-reasoning', 0.5, 2000),
            ('research_fact_check', 'xai', 'grok-4-1-fast-reasoning', 0.2, 1000),
            # Future operations
            ('search_venues', 'anthropic', 'claude-haiku-4-5-20251001', 0.3, 1000),
            ('general_assistant', 'anthropic', 'claude-sonnet-4-20250514', 0.7, 2000),
        ]

        for operation, provider_name, model_id, temperature, max_tokens in default_configs:
            if dry_run:
                # Get operation display name
                display = dict(AIOperationConfig.OPERATION_CHOICES).get(operation, operation)
                self.stdout.write(f"  Would configure: {display} -> {model_id}")
            else:
                try:
                    model = AIModel.objects.get(
                        provider__name=provider_name,
                        model_id=model_id
                    )
                    config, created = AIOperationConfig.objects.update_or_create(
                        operation=operation,
                        defaults={
                            'model': model,
                            'temperature': temperature,
                            'max_tokens': max_tokens,
                            'is_enabled': True,
                        }
                    )
                    status = 'Created' if created else 'Updated'
                    self.stdout.write(f"  {status}: {config.get_operation_display()} -> {model_id}")
                except AIModel.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Skipped: {operation} - Model not found: {provider_name}/{model_id}"
                        )
                    )
