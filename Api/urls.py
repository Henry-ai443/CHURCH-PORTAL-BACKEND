from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

"""
API ENPOINTS
"""
urlpatterns = [
    path('announcements/latest/', views.AnnouncementListApiView.as_view(), name="announcements"),
    path('announcements/all/', views.AllAnnouncementsView.as_view(), name="all_announcements"),
    path('events/', views.EventListView.as_view(), name="event-list"),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('profile/me/', views.UserProfileAPIView.as_view(), name="profile"),
    path('profile/change_password/', views.ChangePasswordAPIView.as_view(), name="change_password"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)