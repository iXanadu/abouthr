"""
Guide Domain Models for Hampton Roads Relocation Guide

This app contains all content models for the About Hampton Roads guide.
These are single-tenant (shared) models - not scoped per account.
All models inherit from BaseModel for timestamps.
"""

from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class Region(BaseModel):
    """
    Peninsula vs Southside - the two main geographic regions of Hampton Roads.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class City(BaseModel):
    """
    The 9 Hampton Roads cities: Virginia Beach, Norfolk, Chesapeake,
    Newport News, Hampton, Portsmouth, Suffolk, Williamsburg, Poquoson.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='cities'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='guide/cities/',
        null=True,
        blank=True
    )
    school_url = models.URLField(
        blank=True,
        help_text="Link to city's public school district website"
    )
    has_beaches = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['region__order', 'order', 'name']
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Venue(BaseModel):
    """
    Unified model for all venue types: restaurants, cafes/breweries,
    attractions, events, and beaches.

    Using a single model with venue_type field instead of 5 separate models
    because of 90% field overlap, simpler CMS interface, and easier filtering.
    """
    VENUE_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('cafe_brewery', 'Cafe/Brewery'),
        ('attraction', 'Attraction'),
        ('event', 'Event'),
        ('beach', 'Beach'),
    ]

    CUISINE_TYPE_CHOICES = [
        ('american', 'American'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('asian', 'Asian'),
        ('seafood', 'Seafood'),
        ('bbq', 'BBQ'),
        ('pizza', 'Pizza'),
        ('breakfast', 'Breakfast/Brunch'),
        ('coffee', 'Coffee/Cafe'),
        ('brewery', 'Brewery'),
        ('fine_dining', 'Fine Dining'),
        ('casual', 'Casual Dining'),
        ('fast_casual', 'Fast Casual'),
        ('other', 'Other'),
    ]

    DATA_SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('google', 'Google Places'),
        ('yelp', 'Yelp Fusion'),
    ]

    ENRICHMENT_STATUS_CHOICES = [
        ('none', 'Not Enriched'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('manual_review', 'Needs Review'),
    ]

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='venues'
    )
    venue_type = models.CharField(
        max_length=20,
        choices=VENUE_TYPE_CHOICES,
        db_index=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Restaurant/Cafe specific
    cuisine_type = models.CharField(
        max_length=20,
        choices=CUISINE_TYPE_CHOICES,
        blank=True,
        help_text="Only for restaurants/cafes"
    )

    # Location
    address = models.CharField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Geo-coordinates for future maps
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Media
    image = models.ImageField(
        upload_to='guide/venues/',
        null=True,
        blank=True
    )

    # Display
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # API Integration IDs
    google_place_id = models.CharField(max_length=255, blank=True, db_index=True)
    yelp_business_id = models.CharField(max_length=255, blank=True, db_index=True)

    # Enrichment data from APIs
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, null=True, blank=True,
        help_text="Average rating (e.g., 4.5)"
    )
    rating_count = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Number of reviews/ratings"
    )
    price_level = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Price level 1-4 ($ to $$$$)"
    )
    hours_json = models.JSONField(
        null=True, blank=True,
        help_text="Opening hours from API"
    )
    photos_json = models.JSONField(
        null=True, blank=True,
        help_text="Photo references from API"
    )

    # Data source tracking
    data_source = models.CharField(
        max_length=20,
        choices=DATA_SOURCE_CHOICES,
        default='manual'
    )
    last_enriched_at = models.DateTimeField(null=True, blank=True)
    enrichment_status = models.CharField(
        max_length=20,
        choices=ENRICHMENT_STATUS_CHOICES,
        default='none'
    )

    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['city', 'venue_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_venue_type_display()})"

    @property
    def price_level_display(self):
        """Return price level as dollar signs."""
        if self.price_level:
            return '$' * self.price_level
        return None

    @property
    def is_enriched(self):
        """Check if venue has been enriched with API data."""
        return self.enrichment_status == 'success'

    @property
    def needs_refresh(self):
        """Check if venue data is stale (older than 7 days)."""
        if not self.last_enriched_at:
            return True
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.last_enriched_at > timedelta(days=7)


class MilitaryBase(BaseModel):
    """
    Military installations in the Hampton Roads area.
    """
    BRANCH_CHOICES = [
        ('navy', 'Navy'),
        ('army', 'Army'),
        ('air_force', 'Air Force'),
        ('coast_guard', 'Coast Guard'),
        ('marines', 'Marines'),
        ('joint', 'Joint Base'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    description = models.TextField(blank=True)
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='military_bases',
        null=True,
        blank=True
    )
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='guide/military/',
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'military bases'

    def __str__(self):
        return f"{self.name} ({self.get_branch_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tunnel(BaseModel):
    """
    The 6 tunnel systems connecting different parts of Hampton Roads.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    connects_from = models.CharField(
        max_length=255,
        help_text="Starting point/city"
    )
    connects_to = models.CharField(
        max_length=255,
        help_text="Ending point/city"
    )
    length_info = models.CharField(
        max_length=100,
        blank=True,
        help_text="Length or travel time info"
    )
    toll_info = models.CharField(
        max_length=255,
        blank=True,
        help_text="Toll pricing information"
    )
    image = models.ImageField(
        upload_to='guide/tunnels/',
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VacationDestination(BaseModel):
    """
    Nearby vacation destinations and getaways from Hampton Roads.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    distance_description = models.CharField(
        max_length=255,
        help_text="e.g., '2 hours south' or '45 minutes west'"
    )
    highlights = models.TextField(
        blank=True,
        help_text="Key attractions or activities"
    )
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='guide/destinations/',
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VendorUtility(BaseModel):
    """
    Utility and vendor contacts per city (internet, electric, water, etc.)
    """
    CATEGORY_CHOICES = [
        ('electric', 'Electric'),
        ('gas', 'Gas'),
        ('water', 'Water/Sewer'),
        ('trash', 'Trash Collection'),
        ('internet', 'Internet'),
        ('cable', 'Cable TV'),
        ('phone', 'Phone'),
        ('other', 'Other'),
    ]

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='vendor_utilities'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['city', 'category', 'order', 'name']
        verbose_name_plural = 'vendor utilities'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.city.name}"


class Testimonial(BaseModel):
    """
    Client quotes and testimonials.
    """
    client_name = models.CharField(max_length=255)
    quote = models.TextField()
    client_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., 'Relocated from California'"
    )
    photo = models.ImageField(
        upload_to='guide/testimonials/',
        null=True,
        blank=True
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']

    def __str__(self):
        return f"{self.client_name}: \"{self.quote[:50]}...\""


class TeamMember(BaseModel):
    """
    Company team members displayed on the About page.
    """
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to='guide/team/',
        null=True,
        blank=True
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.title}"


class VenueAPIConfig(BaseModel):
    """
    Configuration for venue enrichment APIs (Google Places, Yelp, etc.).

    Stores API settings, rate limiting info, and sync preferences.
    """
    PROVIDER_CHOICES = [
        ('google', 'Google Places'),
        ('yelp', 'Yelp Fusion'),
    ]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        unique=True
    )
    is_enabled = models.BooleanField(
        default=False,
        help_text="Enable this API provider"
    )
    api_key_name = models.CharField(
        max_length=100,
        help_text="Key name in .keys file (e.g., GOOGLE_PLACES_API_KEY)"
    )

    # Rate limiting
    daily_quota = models.PositiveIntegerField(
        default=10000,
        help_text="Maximum API calls per day"
    )
    requests_today = models.PositiveIntegerField(
        default=0,
        help_text="API calls made today"
    )
    quota_reset_date = models.DateField(
        auto_now_add=True,
        help_text="Date when requests_today resets"
    )

    # Sync settings
    last_full_sync = models.DateTimeField(
        null=True, blank=True,
        help_text="Last time a full sync was performed"
    )
    venues_per_city = models.PositiveIntegerField(
        default=20,
        help_text="Top N venues to fetch per city during discovery"
    )

    class Meta:
        verbose_name = "Venue API Configuration"
        verbose_name_plural = "Venue API Configurations"

    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return f"{self.get_provider_display()} ({status})"

    def increment_requests(self):
        """Increment the daily request counter, resetting if needed."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.quota_reset_date != today:
            self.requests_today = 0
            self.quota_reset_date = today
        self.requests_today += 1
        self.save(update_fields=['requests_today', 'quota_reset_date'])

    @property
    def quota_remaining(self):
        """Return remaining API calls for today."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.quota_reset_date != today:
            return self.daily_quota
        return max(0, self.daily_quota - self.requests_today)

    @property
    def has_quota(self):
        """Check if there's remaining quota for today."""
        return self.quota_remaining > 0


class PulseContent(models.Model):
    """
    Cached pulse content - trends and headlines for Hampton Roads Pulse.
    One active record per content type at a time.
    """
    CONTENT_TYPES = [
        ('trends', 'X Trends'),
        ('headlines', 'Local Headlines'),
    ]

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_json = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    model_used = models.CharField(max_length=100, blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = "Pulse Content"
        verbose_name_plural = "Pulse Content"
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_content_type_display()} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def get_current(cls, content_type, include_stale=True):
        """
        Get current active content.

        Args:
            content_type: 'trends' or 'headlines'
            include_stale: If True (default), return expired content as fallback.
                          Content should always be visible to users.

        Returns:
            PulseContent instance or None
        """
        from django.utils import timezone
        now = timezone.now()

        # First try to get fresh content
        fresh = cls.objects.filter(
            content_type=content_type,
            is_active=True,
            expires_at__gt=now
        ).first()

        if fresh:
            return fresh

        # If include_stale, return most recent content even if expired
        if include_stale:
            return cls.objects.filter(
                content_type=content_type,
                is_active=True
            ).first()

        return None

    @property
    def is_stale(self):
        """Check if this content has expired (but is still being shown)."""
        from django.utils import timezone
        return self.expires_at <= timezone.now()
