from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

"""
API ENPOINTS - Shared/Common functionality
"""
urlpatterns = [
    # Youth Message Endpoints
    path('youth/messages/create/', views.YouthMessageCreateView.as_view(), name="create_youth_message"),
    path('youth/messages/answered/', views.YouthAnsweredMessagesView.as_view(), name="answered_youth_messages"),
    path('youth/messages/unanswered/', views.YouthUnansweredMessagesView.as_view(), name="unanswered_youth_messages"),
    path('youth/messages/<int:pk>/answer/', views.YouthMessageAnswerView.as_view(), name="answer_youth_message"),

    # ROOM CHATS ENDPOINT
    path('chat/messages/', views.ChatMessageAPIVIEW.as_view(), name="chat_messages"),

    # ADMIN ENDPOINTS
    path('registered_users/', views.RegisteredMembers.as_view(), name="registered_users"),

    # UTILITIES
    path("quizes/fetch/", views.FetchQuizAPIView.as_view(), name="quiz-fetch"),
    path("daily-verse/", views.DailyVerseAPIView.as_view(), name="daily-verse")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)