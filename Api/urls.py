from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('announcements/latest/', views.AnnouncementListApiView.as_view(), name="announcements"),
    path('announcements/all/', views.AllAnnouncementsView.as_view(), name="all_announcements"),
    path('events/', views.EventListView.as_view(), name="event-list"),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)