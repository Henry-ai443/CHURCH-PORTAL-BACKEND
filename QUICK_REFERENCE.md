# Refactoring Quick Reference

## Before vs After

### BEFORE: Monolithic Structure
```
Api/
├── models.py (5 models)
├── serializers.py (8 serializers)
├── views.py (25+ views, 560 lines)
├── urls.py (20+ endpoints)
└── admin.py
```

### AFTER: Modular Structure
```
Api/
├── models.py (5 shared models - unchanged)
├── serializers.py (3 shared serializers)
├── views.py (9 shared views - 200 lines)
├── urls.py (8 shared endpoints)
└── admin.py

authentication/
├── serializers.py (2 serializers)
├── views.py (5 views)
├── urls.py (5 endpoints)
└── [admin.py, models.py, apps.py]

announcements/
├── serializers.py (1 serializer)
├── views.py (4 views)
├── urls.py (8 endpoints)
└── [admin.py, models.py, apps.py]

events/
├── serializers.py (1 serializer)
├── views.py (6 views)
├── urls.py (8 endpoints)
└── [admin.py, models.py, apps.py]
```

---

## App Responsibilities Matrix

| App | Models | Serializers | Views | URL Paths | Purpose |
|-----|--------|-------------|-------|-----------|---------|
| **Api** | 5 | 3 | 9 | 8 | Shared models, youth messages, chat, utilities |
| **authentication** | - | 2 | 5 | 5 | User registration, login, profile management |
| **announcements** | - | 1 | 4 | 8 | Announcement creation, retrieval, management |
| **events** | - | 1 | 6 | 8 | Event creation, retrieval, management |

---

## URL Namespace Organization

### All endpoints are under `/api/` prefix:

```
/api/
├── register/                          → authentication
├── login/                             → authentication
├── current_user/                      → authentication
├── profile/me/                        → authentication
├── profile/change_password/           → authentication
├── announcements/latest/              → announcements
├── announcements/all/                 → announcements
├── admin/announcements/               → announcements
├── admin/announcements/<pk>/          → announcements
├── events/                            → events
├── events/<pk>/                       → events
├── admin/events/                      → events
├── admin/events/<pk>/                 → events
├── youth/messages/create/             → Api (shared)
├── youth/messages/answered/           → Api (shared)
├── youth/messages/unanswered/         → Api (shared)
├── youth/messages/<pk>/answer/        → Api (shared)
├── chat/messages/                     → Api (shared)
├── registered_users/                  → Api (shared)
├── quizes/fetch/                      → Api (shared)
└── daily-verse/                       → Api (shared)
```

---

## Import Path Changes

### Example: Announcement serializer usage

**Before:**
```python
from Api.serializers import AnnouncementSerializer
```

**After:**
```python
from announcements.serializers import AnnouncementSerializer
```

### Example: Event views

**Before:**
```python
from Api.views import EventListView, EventDetailView
```

**After:**
```python
from events.views import EventListView, EventDetailView
```

---

## Permission Classes by App

### authentication/views.py
- `AllowAny` - Registration, Login
- `IsAuthenticated` - Profile management
- `IsAdminUser` - (inherited from DRF)

### announcements/views.py
- `IsAuthenticated` - View announcements
- `IsAdminUser` + `IsAuthenticated` - CRUD announcements
- Custom: `IsStaffUser` (inherits from `IsAdminUser`)

### events/views.py
- `IsAuthenticated` - View events
- `IsStaffUser` - Create/Update/Delete events
- `IsAdminUser` + `IsAuthenticated` - Admin operations
- Custom: `IsStaffUser`

### Api/views.py (Shared)
- `IsAuthenticated` - Youth messages, Chat
- `IsAdminUser` - Registered members
- `AllowAny` - Public utilities

---

## Configuration Files Updated

✅ `settings.py` - Added 3 new apps to INSTALLED_APPS
✅ `urls.py` - Added 3 new app includes
❌ `models.py` - Unchanged (all models remain in Api app)
❌ `asgi.py` - No changes needed
❌ `wsgi.py` - No changes needed

---

## Database Migrations

**No new migrations required!**

Since all models remain in the Api app:
- Models are unchanged
- No new database schema required
- Existing migrations continue to work
- No migration conflicts

Run migrations as usual:
```bash
python manage.py migrate
```

---

## Development Workflow

### Adding a new endpoint to Events:

1. Create view in `events/views.py`
2. Add serializer in `events/serializers.py` (if needed)
3. Add URL pattern in `events/urls.py`
4. Test with the existing `/api/` prefix

### Modifying an endpoint:

1. Navigate to the appropriate app folder
2. Edit the view/serializer
3. Update URL if endpoint path changes
4. Test the updated endpoint

---

## Testing Strategy

### Unit Tests by App:
```
tests/
├── test_authentication.py
├── test_announcements.py
├── test_events.py
├── test_api.py (shared)
└── test_integration.py
```

### Running tests:
```bash
# All tests
python manage.py test

# Specific app
python manage.py test authentication
python manage.py test announcements
python manage.py test events
python manage.py test Api
```

---

## Performance Considerations

✅ **Smaller modules** - Faster to load specific app code
✅ **Better caching** - Can cache by app functionality
✅ **Reduced memory** - Each app only loads its dependencies
✅ **Parallel processing** - Multiple apps can be scaled independently

---

## Security Notes

✅ Permission classes properly separated by app
✅ Auth checks in place for all endpoints
✅ Staff-only operations clearly marked
✅ Admin operations protected
✅ Public endpoints limited to utilities only

---

## Documentation Files Provided

1. **REFACTORING_GUIDE.md** - Comprehensive documentation
2. **REFACTORING_COMPLETE.md** - Completion summary
3. **This file** - Quick reference guide

---

## Quick Commands

```bash
# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create app (template for future apps)
python manage.py startapp <app_name>

# Check for issues
python manage.py check

# Run tests
python manage.py test
```

---

## Support & Troubleshooting

### Import Errors?
- Verify app is in INSTALLED_APPS in settings.py
- Check relative import paths are correct
- Ensure __init__.py exists in app directories

### URL Not Found?
- Check app urls.py is included in project urls.py
- Verify URL pattern syntax is correct
- Use `python manage.py show_urls` to list all URLs

### Model Errors?
- All models are in Api/models.py
- Run `python manage.py migrate` to apply database changes
- Use `python manage.py makemigrations Api` for new models

---

**Refactored project is ready for development! 🚀**
