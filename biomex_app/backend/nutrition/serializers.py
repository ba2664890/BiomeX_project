from rest_framework import serializers
from .models import FoodItem, Recipe, RecipeIngredient, FoodSubstitution, SeasonalCalendar


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'name_local', 'category', 'description',
            'calories', 'proteins', 'carbs', 'fats', 'fiber',
            'prebiotic_score', 'probiotic', 'anti_inflammatory',
            'season', 'image', 'icon', 'is_active'
        ]


class FoodItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'category', 'prebiotic_score', 'icon', 'image']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    food = FoodItemListSerializer(read_only=True)
    
    class Meta:
        model = RecipeIngredient
        fields = ['food', 'quantity', 'notes']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True, read_only=True)
    total_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'prep_time', 'cook_time',
            'total_time', 'difficulty', 'servings', 'ingredients',
            'instructions', 'tags', 'image', 'microbiome_score', 'is_active'
        ]
    
    def get_total_time(self, obj):
        return obj.prep_time + obj.cook_time


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'prep_time', 'cook_time', 'image', 'microbiome_score']


class FoodSubstitutionSerializer(serializers.ModelSerializer):
    food_to_avoid = FoodItemListSerializer(read_only=True)
    food_to_prefer = FoodItemListSerializer(read_only=True)
    
    class Meta:
        model = FoodSubstitution
        fields = ['id', 'food_to_avoid', 'food_to_prefer', 'impact_score', 'reason']


class SeasonalCalendarSerializer(serializers.ModelSerializer):
    food = FoodItemListSerializer(read_only=True)
    
    class Meta:
        model = SeasonalCalendar
        fields = ['id', 'food', 'month', 'is_in_season', 'region']


class SuperfoodSerializer(serializers.ModelSerializer):
    """Serializer for superfoods with match percentage"""
    match_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'description', 'prebiotic_score',
            'match_percentage', 'image', 'icon'
        ]
    
    def get_match_percentage(self, obj):
        # Calculate match based on prebiotic score
        return min(98, 70 + obj.prebiotic_score // 5)


class FoodToAvoidSerializer(serializers.ModelSerializer):
    """Serializer for foods to avoid with reason"""
    reason = serializers.SerializerMethodField()
    
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'category', 'reason', 'icon']
    
    def get_reason(self, obj):
        if obj.category == 'oil':
            return 'INFLAMMATOIRE'
        return 'À LIMITER'
