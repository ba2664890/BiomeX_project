from django.urls import path
from .views import (
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    UserDashboardView,
    UserNotificationsView,
    MarkNotificationReadView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    path('notifications/', UserNotificationsView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
