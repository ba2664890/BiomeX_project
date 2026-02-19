from rest_framework import serializers
from .models import (
    DailyWellnessCheck,
    HealthMetric,
    SymptomLog,
    WeeklyInsight,
    Routine,
    RoutineLog
)


class DailyWellnessCheckSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = DailyWellnessCheck
        fields = [
            'id', 'date', 'category', 'category_display',
            'rating', 'rating_display', 'notes', 'created_at'
        ]


class HealthMetricSerializer(serializers.ModelSerializer):
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = HealthMetric
        fields = [
            'id', 'metric_type', 'metric_type_display',
            'value', 'unit', 'date', 'notes', 'created_at'
        ]


class SymptomLogSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = SymptomLog
        fields = [
            'id', 'symptom', 'severity', 'severity_display',
            'date', 'duration_hours', 'notes', 'created_at'
        ]


class WeeklyInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyInsight
        fields = [
            'id', 'week_start', 'week_end', 'title',
            'description', 'insight_type', 'related_food',
            'score_change', 'is_read', 'created_at'
        ]


class RoutineSerializer(serializers.ModelSerializer):
    routine_type_display = serializers.CharField(source='get_routine_type_display', read_only=True)
    
    class Meta:
        model = Routine
        fields = [
            'id', 'name', 'routine_type', 'routine_type_display',
            'description', 'time_of_day', 'is_active', 'created_at'
        ]


class RoutineLogSerializer(serializers.ModelSerializer):
    routine = RoutineSerializer(read_only=True)
    
    class Meta:
        model = RoutineLog
        fields = ['id', 'routine', 'date', 'completed', 'notes']


class TrackingDashboardSerializer(serializers.Serializer):
    """Serializer for tracking dashboard data"""
    current_score = serializers.IntegerField()
    score_change = serializers.IntegerField()
    score_history = serializers.ListField()
    wellness_categories = serializers.ListField()
    next_test_days = serializers.IntegerField()
    weekly_insights = WeeklyInsightSerializer(many=True)
    routines = RoutineSerializer(many=True)


class WellnessSummarySerializer(serializers.Serializer):
    """Summary of wellness checks by category"""
    category = serializers.CharField()
    category_display = serializers.CharField()
    average_rating = serializers.FloatField()
    check_count = serializers.IntegerField()
    trend = serializers.CharField()
