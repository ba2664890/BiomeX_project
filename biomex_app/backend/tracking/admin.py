from django.contrib import admin
from .models import (
    DailyWellnessCheck,
    HealthMetric,
    SymptomLog,
    WeeklyInsight,
    Routine,
    RoutineLog
)


@admin.register(DailyWellnessCheck)
class DailyWellnessCheckAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'category', 'rating', 'created_at']
    list_filter = ['category', 'rating', 'date']
    search_fields = ['user__email', 'notes']
    ordering = ['-date']


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric_type', 'value', 'unit', 'date']
    list_filter = ['metric_type', 'date']
    search_fields = ['user__email', 'notes']
    ordering = ['-date']


@admin.register(SymptomLog)
class SymptomLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'symptom', 'severity', 'date']
    list_filter = ['severity', 'date']
    search_fields = ['user__email', 'symptom', 'notes']
    ordering = ['-date']


@admin.register(WeeklyInsight)
class WeeklyInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'insight_type', 'is_read', 'created_at']
    list_filter = ['insight_type', 'is_read']
    search_fields = ['user__email', 'title', 'description']
    ordering = ['-created_at']


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'routine_type', 'time_of_day', 'is_active']
    list_filter = ['routine_type', 'is_active']
    search_fields = ['user__email', 'name']


@admin.register(RoutineLog)
class RoutineLogAdmin(admin.ModelAdmin):
    list_display = ['routine', 'date', 'completed']
    list_filter = ['completed', 'date']
