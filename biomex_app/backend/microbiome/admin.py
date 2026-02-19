from django.contrib import admin
from .models import MicrobiomeAnalysis, BacteriaBalance, HealthMarker, AnalysisHistory


class BacteriaBalanceInline(admin.TabularInline):
    model = BacteriaBalance
    extra = 0


class HealthMarkerInline(admin.TabularInline):
    model = HealthMarker
    extra = 0


@admin.register(MicrobiomeAnalysis)
class MicrobiomeAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'sample_id', 'user', 'status', 'overall_score',
        'species_count', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['sample_id', 'user__email']
    inlines = [BacteriaBalanceInline, HealthMarkerInline]
    ordering = ['-created_at']


@admin.register(BacteriaBalance)
class BacteriaBalanceAdmin(admin.ModelAdmin):
    list_display = ['bacteria_name', 'analysis', 'percentage', 'status']
    list_filter = ['status', 'bacteria_type']
    search_fields = ['bacteria_name', 'analysis__sample_id']


@admin.register(HealthMarker)
class HealthMarkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'analysis', 'category', 'score', 'status']
    list_filter = ['category', 'status']
    search_fields = ['name', 'analysis__sample_id']


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'overall_score']
    list_filter = ['date']
    search_fields = ['user__email']
    ordering = ['-date']
