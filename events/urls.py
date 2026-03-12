from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventListView.as_view(), name="event-list"),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('admin/events/', views.AdminEventView.as_view(), name="adminEvent"),
    path('admin/events/<int:pk>/', views.AdminEventDetailView.as_view(), name="adminEventDetail"),
]
