from django.contrib import admin
from .models import Recommendation, DailyRecommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'title', 'category', 'priority',
        'is_read', 'is_completed', 'created_at'
    ]
    list_filter = ['category', 'priority', 'is_read', 'is_completed']
    search_fields = ['user__email', 'title', 'description']
    ordering = ['-created_at']


@admin.register(DailyRecommendation)
class DailyRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'start_date', 'end_date']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
