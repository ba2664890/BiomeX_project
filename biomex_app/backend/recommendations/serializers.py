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


class RAGChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=4000)
    top_k = serializers.IntegerField(min_value=1, max_value=20, required=False, default=6)
    namespace = serializers.CharField(max_length=100, required=False, allow_blank=True)


class RAGCustomDocumentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300, required=False, allow_blank=True)
    text = serializers.CharField(max_length=12000)
    metadata = serializers.DictField(required=False, default=dict)


class RAGIngestRequestSerializer(serializers.Serializer):
    source = serializers.ChoiceField(choices=["nutrition_db", "csv", "custom"])
    namespace = serializers.CharField(max_length=100, required=False, allow_blank=True)
    csv_path = serializers.CharField(max_length=500, required=False, allow_blank=True)
    csv_text_column = serializers.CharField(max_length=200, required=False, allow_blank=True)
    documents = serializers.ListField(
        child=RAGCustomDocumentSerializer(),
        required=False,
        default=list,
    )

    def validate(self, attrs):
        source = attrs.get("source")
        if source == "csv" and not attrs.get("csv_path"):
            raise serializers.ValidationError({"csv_path": "csv_path est requis pour source='csv'."})
        if source == "custom" and not attrs.get("documents"):
            raise serializers.ValidationError({"documents": "documents est requis pour source='custom'."})
        return attrs
