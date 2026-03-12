from django.urls import path
from . import views

urlpatterns = [
    path('announcements/latest/', views.AnnouncementListApiView.as_view(), name="announcements"),
    path('announcements/all/', views.AllAnnouncementsView.as_view(), name="all_announcements"),
    path('admin/announcements/', views.AdminAnnouncementView.as_view(), name="adminAnnouncement"),
    path('admin/announcements/<int:pk>/', views.AdminAnnouncementDetailView.as_view(), name="adminAnnouncementDetail"),
]
