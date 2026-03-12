from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('current_user/', views.CurrentUserAPIView.as_view(), name="currentUser"),
    path('profile/me/', views.UserProfileAPIView.as_view(), name="profile"),
    path('profile/change_password/', views.ChangePasswordAPIView.as_view(), name="change_password"),
]
