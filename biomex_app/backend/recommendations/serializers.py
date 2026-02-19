from rest_framework import serializers
from .models import Recommendation, DailyRecommendation
from nutrition.serializers import FoodItemListSerializer, RecipeListSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    related_food = FoodItemListSerializer(read_only=True)
    related_recipe = RecipeListSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'related_food', 'related_recipe',
            'expected_score_improvement', 'is_read', 'is_completed',
            'completed_at', 'created_at', 'expires_at'
        ]


class RecommendationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'title', 'category', 'category_display',
            'priority', 'is_read', 'created_at'
        ]


class DailyRecommendationSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    related_food = FoodItemListSerializer(read_only=True)
    
    class Meta:
        model = DailyRecommendation
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'related_food', 'icon', 'is_active'
        ]


class MarkRecommendationCompletedSerializer(serializers.Serializer):
    recommendation_id = serializers.IntegerField()
    completed = serializers.BooleanField(default=True)
