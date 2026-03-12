# Django Church Portal Backend - Refactored Structure

## Overview
This document outlines the refactored Django REST Framework project structure with separated apps for better modularity and maintainability.

## Project Structure

```
CHURCH-PORTAL-BACKEND/
├── Api/                           # Core/Shared app
│   ├── migrations/
│   ├── models.py                  # Shared models: Announcement, Event, Profile, YouthMessage, ChatMessage
│   ├── serializers.py             # Shared serializers: YouthMessageSerializer, ChatMessageSerializer, MembersSerializer
│   ├── views.py                   # Shared views: Youth messages, Chat, Utilities, Registered members
│   ├── urls.py                    # Shared endpoints
│   ├── apps.py
│   └── admin.py
│
├── authentication/                # Authentication app
│   ├── migrations/
│   ├── models.py                  # (empty - uses shared models)
│   ├── serializers.py             # RegisterSerializer, ProfileSerializer
│   ├── views.py                   # RegisterView, LoginView, UserProfileAPIView, ChangePasswordAPIView, CurrentUserAPIView
│   ├── urls.py                    # Authentication endpoints
│   ├── apps.py
│   └── admin.py
│
├── announcements/                 # Announcements app
│   ├── migrations/
│   ├── models.py                  # (empty - uses shared models)
│   ├── serializers.py             # AnnouncementSerializer
│   ├── views.py                   # Announcement views for public and admin
│   ├── urls.py                    # Announcement endpoints
│   ├── apps.py
│   └── admin.py
│
├── events/                        # Events app
│   ├── migrations/
│   ├── models.py                  # (empty - uses shared models)
│   ├── serializers.py             # EventSerializer
│   ├── views.py                   # Event views for public and admin
│   ├── urls.py                    # Event endpoints
│   ├── apps.py
│   └── admin.py
│
├── church_portal_backend/         # Project settings
│   ├── settings.py                # Updated with all 4 apps
│   ├── urls.py                    # Updated with all app includes
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
│
├── manage.py
├── requirements.txt
└── Procfile
```

## Apps Description

### 1. **Api** (Core/Shared App)
**Purpose:** Contains shared models and common functionality

**Models:**
- `Announcement` - Church announcements
- `Event` - Church events
- `Profile` - User profile extension
- `YouthMessage` - Youth message submission
- `ChatMessage` - Chat messages

**Views:**
- Youth message creation and management
- Chat message retrieval
- Quiz fetching
- Daily verse retrieval
- Registered members list

**Endpoints:**
```
POST   /api/youth/messages/create/
GET    /api/youth/messages/answered/
GET    /api/youth/messages/unanswered/
POST   /api/youth/messages/<pk>/answer/
GET    /api/chat/messages/
GET    /api/registered_users/
GET    /api/quizes/fetch/
GET    /api/daily-verse/
```

---

### 2. **Authentication** App
**Purpose:** User registration, login, profile management, and authentication

**Models:** None (uses shared `Profile` and Django `User`)

**Serializers:**
- `RegisterSerializer` - User registration with country field
- `ProfileSerializer` - User profile data

**Views:**
- `RegisterView` - User registration
- `LoginView` - User login with token authentication
- `CurrentUserAPIView` - Get current user info
- `UserProfileAPIView` - Get/update user profile
- `ChangePasswordAPIView` - Change user password
- `IsStaffUser` - Permission class for staff-only access

**Endpoints:**
```
POST   /api/register/
POST   /api/login/
GET    /api/current_user/
GET    /api/profile/me/
PUT    /api/profile/me/
PATCH  /api/profile/me/
POST   /api/profile/change_password/
```

---

### 3. **Announcements** App
**Purpose:** Management of church announcements

**Models:** None (uses shared `Announcement`)

**Serializers:**
- `AnnouncementSerializer` - Announcement data

**Views:**
- `AnnouncementListApiView` - Get latest 3 announcements
- `AllAnnouncementsView` - Get all announcements
- `AdminAnnouncementView` - Admin CRUD for announcements
- `AdminAnnouncementDetailView` - Admin detail view/update/delete

**Endpoints:**
```
GET    /api/announcements/latest/
GET    /api/announcements/all/
POST   /api/announcements/all/
GET    /api/admin/announcements/
POST   /api/admin/announcements/
GET    /api/admin/announcements/<pk>/
PUT    /api/admin/announcements/<pk>/
PATCH  /api/admin/announcements/<pk>/
DELETE /api/admin/announcements/<pk>/
```

---

### 4. **Events** App
**Purpose:** Management of church events

**Models:** None (uses shared `Event`)

**Serializers:**
- `EventSerializer` - Event data

**Views:**
- `EventListView` - Get all events / Create event
- `EventDetailView` - Get/Update/Delete event
- `AdminEventView` - Admin event list/create
- `AdminEventDetailView` - Admin detail view/update/delete
- `IsStaffUser` - Permission class for staff-only access

**Endpoints:**
```
GET    /api/events/
POST   /api/events/
GET    /api/events/<pk>/
PUT    /api/events/<pk>/
PATCH  /api/events/<pk>/
DELETE /api/events/<pk>/
GET    /api/admin/events/
POST   /api/admin/events/
GET    /api/admin/events/<pk>/
PUT    /api/admin/events/<pk>/
PATCH  /api/admin/events/<pk>/
DELETE /api/admin/events/<pk>/
```

---

## Key Benefits of This Structure

1. **Separation of Concerns** - Each app has a specific responsibility
2. **Scalability** - Easy to add new features to individual apps
3. **Maintainability** - Clear organization makes code easier to understand
4. **Reusability** - Serializers and views are organized by domain
5. **Testing** - Easier to write tests for isolated app functionality
6. **Collaboration** - Multiple developers can work on different apps simultaneously

## Migrations

Since the models remain in the `Api` app, all migrations are managed there:

```bash
python manage.py makemigrations Api
python manage.py migrate
```

The other apps (`authentication`, `announcements`, `events`) don't have their own models and only reference the shared models from `Api`.

## URL Routing

The project-level `urls.py` includes all app URLs under the `/api/` prefix:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view, name='root'),
    path('api/', include('Api.urls')),                      # Shared endpoints
    path('api/', include('authentication.urls')),           # Auth endpoints
    path('api/', include('announcements.urls')),            # Announcement endpoints
    path('api/', include('events.urls')),                   # Event endpoints
]
```

## Permission Classes

### Authentication App
- `AllowAny` - Registration and Login
- `IsAuthenticated` - Profile management
- `IsAdminUser` - Admin functions

### Announcements App
- `IsAuthenticated` - View announcements
- `IsAdminUser` + `IsAuthenticated` - Admin CRUD

### Events App
- `IsAuthenticated` - View events
- `IsStaffUser` (custom) - Create/Modify/Delete events
- `IsAdminUser` + `IsAuthenticated` - Admin functions

### Api App (Shared)
- `IsAuthenticated` - Youth messages, Chat
- `IsAdminUser` - Registered members, Admin functions
- `AllowAny` - Quiz, Daily verse

## Testing the Refactored Structure

To test the new structure:

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Test endpoints
curl http://localhost:8000/api/register/
curl http://localhost:8000/api/login/
curl http://localhost:8000/api/events/
curl http://localhost:8000/api/announcements/latest/
```

## Environment Variables

Ensure all required environment variables are set:

- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection URL
- `RESEND_API_KEY` - Email service API key
- `CLOUD_NAME` - Cloudinary cloud name
- `API_KEY` - Cloudinary API key
- `API_SECRET` - Cloudinary API secret
- `DEFAULT_FROM_EMAIL` - Default email sender
- `REDIS_URL` - Redis connection URL

## Notes

- Models are shared in the `Api` app to avoid duplication and maintain referential integrity
- Each app has its own serializers and views for better organization
- All authentication logic is centralized in the `authentication` app
- Admin views are replicated in their respective feature apps for easier management
- The `IsStaffUser` permission class is used for staff-level operations

## Future Improvements

- Add authentication middleware for enhanced security
- Implement API rate limiting
- Add comprehensive API documentation (Swagger/OpenAPI)
- Implement caching for frequently accessed data
- Add more granular permission classes for specific operations
- Consider moving shared views/serializers to a utils module
