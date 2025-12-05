from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

"""
API ENPOINTS
"""
urlpatterns = [
    #GENERAL INFO ENDPOINTS
    path('announcements/latest/', views.AnnouncementListApiView.as_view(), name="announcements"),
    path('announcements/all/', views.AllAnnouncementsView.as_view(), name="all_announcements"),
    path('events/', views.EventListView.as_view(), name="event-list"),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),

    #AUTHENTICATION ENDPOINTS
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('current_user/', views.CurrentUserAPIView.as_view(), name="currentUser"),

    #USER ENDPOITNS
    path('profile/me/', views.UserProfileAPIView.as_view(), name="profile"),
    path('profile/change_password/', views.ChangePasswordAPIView.as_view(), name="change_password"),

    # Youth Message Endpoints
    path('youth/messages/create/', views.YouthMessageCreateView.as_view(), name="create_youth_message"),
    path('youth/messages/answered/', views.YouthAnsweredMessagesView.as_view(), name="answered_youth_messages"),
    path('youth/messages/unanswered/', views.YouthUnansweredMessagesView.as_view(), name="unanswered_youth_messages"),
    path('youth/messages/<int:pk>/answer/', views.YouthMessageAnswerView.as_view(), name="answer_youth_message"),


    # ROOM CHATS ENPOINT
    path('chat/messages/', views.ChatMessageAPIVIEW.as_view(), name="chat_messages"),


    #ADMIN ENDPOINTS
    path('registered_users/', views.RegisteredMembers.as_view(), name="registered_users"),
    path("admin/announcements/", views.AdminAnnouncementView.as_view(), name="adminAnnouncement"),
    path("admin/announcements/<int:pk>/", views.AdminAnnouncementDetailView.as_view(), name="adminAnnouncement"),
    path("admin/events/<int:pk>/", views.AdminEventDetailView.as_view(), name="adminEvent"),
    path("admin/events/", views.AdminEventView.as_view(), name="adminEvent"),

    #UTILITIES
    path("quizes/fetch/", views.FetchQuizAPIView.as_view(), name="quiz-fetch"),
    path("daily-verse/", views.DailyVerseAPIView.as_view(), name="daily-verse")
    



] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)