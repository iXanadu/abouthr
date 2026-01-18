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

    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['city', 'venue_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_venue_type_display()})"


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
