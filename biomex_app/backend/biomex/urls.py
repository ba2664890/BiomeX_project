"""
URL configuration for biomex project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public health check
    path('api/health/', health_check, name='health-check'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Endpoints
    path('api/users/', include('users.urls')),
    path('api/microbiome/', include('microbiome.urls')),
    path('api/nutrition/', include('nutrition.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/site-content/', include('site_content.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
