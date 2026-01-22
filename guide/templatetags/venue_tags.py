"""
Template tags for venue display.
"""

from datetime import datetime
from django import template

register = template.Library()


@register.filter
def is_open_now(venue):
    """
    Check if a venue is currently open based on hours_json.
    Returns True, False, or None if we can't determine.
    """
    if not venue.hours_json:
        return None

    periods = venue.hours_json.get('periods', [])
    if not periods:
        return None

    now = datetime.now()
    current_day = now.weekday()  # Monday=0, Sunday=6
    # Google uses Sunday=0, so convert
    google_day = (current_day + 1) % 7
    current_time = now.strftime('%H%M')

    for period in periods:
        open_info = period.get('open', {})
        close_info = period.get('close', {})

        open_day = open_info.get('day')
        open_time = open_info.get('time', '0000')
        close_day = close_info.get('day', open_day)
        close_time = close_info.get('time', '2359')

        # Handle 24-hour places
        if not close_info:
            return True

        if open_day == google_day:
            if open_time <= current_time <= close_time:
                return True

    return False


@register.filter
def todays_hours(venue):
    """
    Get today's hours as a readable string.
    """
    if not venue.hours_json:
        return None

    descriptions = venue.hours_json.get('weekdayDescriptions', [])
    if not descriptions:
        return None

    now = datetime.now()
    weekday = now.weekday()  # Monday=0

    if weekday < len(descriptions):
        # Parse out just the hours part
        desc = descriptions[weekday]
        if ':' in desc:
            return desc.split(':', 1)[1].strip()
        return desc

    return None


@register.filter
def star_display(rating):
    """
    Convert rating to star display.
    Returns HTML for filled and empty stars.
    """
    if not rating:
        return ''

    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.3
    empty_stars = 5 - full_stars - (1 if has_half else 0)

    html = '<i class="bi bi-star-fill text-warning"></i>' * full_stars
    if has_half:
        html += '<i class="bi bi-star-half text-warning"></i>'
    html += '<i class="bi bi-star text-warning opacity-25"></i>' * empty_stars

    return html


@register.filter
def format_review_count(count):
    """Format review count for display (e.g., 1.2k)."""
    if not count:
        return ''
    if count >= 1000:
        return f'{count/1000:.1f}k'
    return str(count)


@register.simple_tag
def venue_badge_class(venue):
    """Return CSS class for venue rating badge."""
    if not venue.rating:
        return 'bg-secondary'
    if venue.rating >= 4.5:
        return 'bg-success'
    if venue.rating >= 4.0:
        return 'bg-primary'
    if venue.rating >= 3.5:
        return 'bg-info'
    return 'bg-secondary'


@register.filter
def has_photo(venue):
    """Check if venue has at least one photo."""
    return bool(venue.photos_json and len(venue.photos_json) > 0)


@register.filter
def photo_count(venue):
    """Return number of photos for a venue."""
    if not venue.photos_json:
        return 0
    return len(venue.photos_json)
