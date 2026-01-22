# Session Progress: Maps & Pulse UI Improvements

**Date:** 2026-01-22
**Duration:** ~30 minutes
**Focus:** Adding map images, improving Pulse widget UX

---

## Session Overview

Added military bases and tunnels maps to their respective pages. Improved the Hampton Roads Pulse widget with collapsible functionality and fixed the staleness issue so content always displays.

### Objectives
1. Add uploaded map images to military and tunnels pages
2. Make Pulse section collapsible with partial-open default
3. Fix Pulse staleness so content always shows (never empty)

---

## Major Accomplishments

### 1. Map Images Added
- **Military Bases Map**: Added to `/military/` page in an info-card container
- **Tunnels/Bridges Map**: Added to `/tunnels/` page in an info-card container
- Images stored in `static/images/maps/` directory
- Responsive sizing with max-width of 800px, centered

### 2. Pulse Widget - Collapsible UI
- **Partial-open default**: Shows first 2 items from each column on load
- **Clickable header**: Top toggle with chevron icon
- **Bottom expand/collapse button**: Wide, centered, pill-shaped button
  - Text changes: "Expand" / "Collapse" based on state
  - Icon rotates with state
- Items beyond first 2 have `.pulse-item-extra` class for toggling

### 3. Pulse Staleness Fix
- Modified `PulseContent.get_current()` to return expired content as fallback
- Added `include_stale=True` parameter (default) to always return content
- Added `is_stale` property to PulseContent model
- Template shows "(updating soon)" indicator when content is stale
- **Result**: Pulse section will never be empty if any content exists

---

## Files Created

```
static/images/maps/military-bases-map.jpg    # Military bases map image
static/images/maps/tunnels-map.jpg           # Tunnels/bridges map image
```

---

## Files Modified

| File | Changes |
|------|---------|
| `guide/models.py` | Added `include_stale` param to `get_current()`, added `is_stale` property |
| `guide/services/pulse_service.py` | Pass `include_stale=True`, return `trends_stale` and `headlines_stale` flags |
| `static/css/style.css` | Added collapsible header styles, bottom toggle button styles |
| `templates/guide/includes/pulse_widget.html` | Complete rewrite with partial collapse, bottom button, JS toggle |
| `templates/guide/military.html` | Added military bases map section |
| `templates/guide/tunnels.html` | Added tunnels/bridges map section |

---

## Architectural Decisions

1. **Partial collapse instead of full hide**: User wanted 1/3 visible on load, not fully collapsed. Used `.pulse-item-extra` class to hide items beyond first 2.

2. **Stale content as fallback**: Rather than showing empty sections, we now always return the most recent content even if expired. The UI indicates staleness with "(updating soon)" text.

3. **Dual toggle controls**: Both header and bottom button toggle the same state for better UX.

---

## Pending / Next Session

### Immediate
- [ ] Test Pulse collapsible on mobile devices
- [ ] Monitor Pulse staleness behavior over time
- [ ] Image optimization (some images up to 1.1MB)

### Production Deployment
- [ ] Configure DNS for abouthamptonroads.com
- [ ] Deploy to production environment
- [ ] SSL certificate setup

---

## Commands Reference

```bash
# Restart service after changes
sudo systemctl restart gunicorn_abouthamptonroads_dev

# Check Pulse status
python manage.py refresh_pulse --stats
```
