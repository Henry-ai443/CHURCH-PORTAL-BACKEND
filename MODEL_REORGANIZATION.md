# Model Organization Update

## Summary
Models have been moved from the shared Api/models.py to their respective app directories for better modularity and separation of concerns.

---

## New Model Organization

### 📁 authentication/models.py
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    unique_id = models.CharField(max_length=20, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
```

### 📁 announcements/models.py
```python
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 📁 events/models.py
```python
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    entry = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)
```

### 📁 Api/models.py (Core/Shared only)
```python
class YouthMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
```

---

## Import Changes

### authentication/serializers.py
```python
# Before
from Api.models import Profile

# After
from .models import Profile
```

### announcements/serializers.py
```python
# Before
from Api.models import Announcement

# After
from .models import Announcement
```

### events/serializers.py
```python
# Before
from Api.models import Event

# After
from .models import Event
```

### authentication/views.py
```python
# Before
from Api.models import Profile

# After
from .models import Profile
```

### announcements/views.py
```python
# Before
from Api.models import Announcement

# After
from .models import Announcement
```

### events/views.py
```python
# Before
from Api.models import Event

# After
from .models import Event
```

---

## Benefits

✅ **Better Separation of Concerns** - Each app owns its models
✅ **Cleaner Dependencies** - No need to import from Api for app-specific models
✅ **Easier Testing** - Can test each app in isolation
✅ **Scalability** - New models naturally belong to their app
✅ **Maintainability** - Clear relationship between models and app logic

---

## Database Migration

⚠️ **IMPORTANT**: Run these commands to update your database:

```bash
# Create migrations for each app
python manage.py makemigrations authentication
python manage.py makemigrations announcements
python manage.py makemigrations events
python manage.py makemigrations Api

# Apply migrations
python manage.py migrate
```

---

## Verification

✅ All model imports updated
✅ All serializer imports updated
✅ All view imports updated
✅ Python syntax verified
✅ No circular dependencies
✅ All files successfully refactored

---

## Complete File Structure

```
authentication/
├── models.py           (Profile)
├── serializers.py      (RegisterSerializer, ProfileSerializer - uses Profile)
├── views.py           (uses Profile from models)
└── urls.py

announcements/
├── models.py          (Announcement)
├── serializers.py     (AnnouncementSerializer - uses Announcement)
├── views.py          (uses Announcement from models)
└── urls.py

events/
├── models.py         (Event)
├── serializers.py    (EventSerializer - uses Event)
├── views.py         (uses Event from models)
└── urls.py

Api/
├── models.py        (YouthMessage, ChatMessage - shared core models)
├── serializers.py   (YouthMessageSerializer, ChatMessageSerializer, MembersSerializer)
├── views.py        (Youth messages, Chat, Utilities)
└── urls.py
```

---

Refactoring completed! Models are now properly organized by app. 🎉
