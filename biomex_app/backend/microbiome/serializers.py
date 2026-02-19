from rest_framework import serializers
from .models import MicrobiomeAnalysis, BacteriaBalance, HealthMarker, AnalysisHistory


class BacteriaBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacteriaBalance
        fields = [
            'id', 'bacteria_name', 'bacteria_type', 
            'percentage', 'status', 'reference_min', 
            'reference_max', 'description'
        ]


class HealthMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMarker
        fields = ['id', 'name', 'category', 'score', 'status', 'description']


class MicrobiomeAnalysisSerializer(serializers.ModelSerializer):
    bacteria_balances = BacteriaBalanceSerializer(many=True, read_only=True)
    health_markers = HealthMarkerSerializer(many=True, read_only=True)
    
    class Meta:
        model = MicrobiomeAnalysis
        fields = [
            'id', 'sample_id', 'sample_date', 'status',
            'overall_score', 'diversity_score', 'inflammation_score', 
            'gut_brain_score', 'species_count', 'probiotic_count',
            'pathogen_percentage', 'shannon_index', 'simpson_index',
            'chao1_index', 'percentile_africa', 'percentile_local',
            'next_test_date', 'summary', 'recommendations',
            'bacteria_balances', 'health_markers',
            'created_at', 'completed_at'
        ]


class MicrobiomeAnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = MicrobiomeAnalysis
        fields = [
            'id', 'sample_id', 'sample_date', 'status',
            'overall_score', 'species_count', 'created_at'
        ]


class AnalysisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisHistory
        fields = [
            'id', 'date', 'overall_score', 'diversity_score',
            'inflammation_score', 'gut_brain_score', 'notes'
        ]


class DashboardScoreSerializer(serializers.Serializer):
    """Serializer for dashboard score data"""
    overall_score = serializers.IntegerField()
    diversity_score = serializers.IntegerField()
    inflammation_score = serializers.IntegerField()
    gut_brain_score = serializers.IntegerField()
    status = serializers.CharField()
    species_count = serializers.IntegerField()
    probiotic_count = serializers.IntegerField()
    pathogen_percentage = serializers.FloatField()
    last_updated = serializers.DateTimeField()


class DetailedAnalysisSerializer(serializers.ModelSerializer):
    """Full detailed analysis with all related data"""
    bacteria_balances = BacteriaBalanceSerializer(many=True, read_only=True)
    health_markers = HealthMarkerSerializer(many=True, read_only=True)
    score_history = AnalysisHistorySerializer(many=True, read_only=True, source='user.score_history')
    
    class Meta:
        model = MicrobiomeAnalysis
        fields = [
            'id', 'sample_id', 'sample_date', 'status',
            'overall_score', 'diversity_score', 'inflammation_score', 
            'gut_brain_score', 'species_count', 'probiotic_count',
            'pathogen_percentage', 'shannon_index', 'simpson_index',
            'chao1_index', 'percentile_africa', 'percentile_local',
            'next_test_date', 'summary', 'recommendations',
            'bacteria_balances', 'health_markers', 'score_history',
            'created_at', 'completed_at'
        ]
