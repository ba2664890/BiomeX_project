from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime
from .models import FoodItem, Recipe, FoodSubstitution, SeasonalCalendar
from .serializers import (
    FoodItemSerializer,
    FoodItemListSerializer,
    RecipeSerializer,
    RecipeListSerializer,
    FoodSubstitutionSerializer,
    SeasonalCalendarSerializer,
    SuperfoodSerializer,
    FoodToAvoidSerializer
)


class FoodSearchView(APIView):
    """Search for food items"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        
        foods = FoodItem.objects.filter(is_active=True)
        
        if query:
            foods = foods.filter(
                Q(name__icontains=query) | 
                Q(name_local__icontains=query) |
                Q(description__icontains=query)
            )
        
        if category:
            foods = foods.filter(category=category)
        
        serializer = FoodItemListSerializer(foods[:20], many=True)
        return Response(serializer.data)


class FoodDetailView(APIView):
    """Get food item details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            food = FoodItem.objects.get(pk=pk, is_active=True)
            serializer = FoodItemSerializer(food)
            return Response(serializer.data)
        except FoodItem.DoesNotExist:
            return Response(
                {'error': 'Aliment non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


class SuperfoodsView(APIView):
    """Get personalized superfoods for the user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get high prebiotic score foods
        superfoods = FoodItem.objects.filter(
            is_active=True,
            prebiotic_score__gte=70
        ).order_by('-prebiotic_score')[:10]
        
        serializer = SuperfoodSerializer(superfoods, many=True)
        return Response(serializer.data)


class FoodsToAvoidView(APIView):
    """Get foods to avoid based on user's microbiome"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get inflammatory foods
        foods_to_avoid = FoodItem.objects.filter(
            is_active=True,
            anti_inflammatory=False,
            category__in=['oil', 'grain']
        ).order_by('?')[:5]
        
        serializer = FoodToAvoidSerializer(foods_to_avoid, many=True)
        return Response(serializer.data)


class RecipeListView(generics.ListAPIView):
    """List all recipes"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Recipe.objects.filter(is_active=True)
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset.order_by('-microbiome_score')


class RecipeDetailView(APIView):
    """Get recipe details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk, is_active=True)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recette non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )


class RecommendedRecipesView(APIView):
    """Get personalized recipe recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get recipes with high microbiome score
        recipes = Recipe.objects.filter(
            is_active=True,
            microbiome_score__gte=75
        ).order_by('-microbiome_score')[:5]
        
        serializer = RecipeListSerializer(recipes, many=True)
        return Response(serializer.data)


class FoodSubstitutionsView(APIView):
    """Get food substitution recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        substitutions = FoodSubstitution.objects.select_related(
            'food_to_avoid', 'food_to_prefer'
        ).order_by('-impact_score')[:10]
        
        serializer = FoodSubstitutionSerializer(substitutions, many=True)
        return Response(serializer.data)


class SeasonalCalendarView(APIView):
    """Get seasonal foods for current month"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        region = request.query_params.get('region', 'Dakar')
        month = int(request.query_params.get('month', datetime.now().month))
        
        seasonal = SeasonalCalendar.objects.filter(
            region=region,
            month=month,
            is_in_season=True
        ).select_related('food')[:10]
        
        serializer = SeasonalCalendarSerializer(seasonal, many=True)
        return Response(serializer.data)


class NutritionDashboardView(APIView):
    """Get all nutrition data for dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Superfoods
        superfoods = FoodItem.objects.filter(
            is_active=True,
            prebiotic_score__gte=70
        ).order_by('-prebiotic_score')[:4]
        
        # Foods to avoid
        foods_to_avoid = FoodItem.objects.filter(
            is_active=True,
            anti_inflammatory=False,
            category__in=['oil', 'grain']
        ).order_by('?')[:4]
        
        # Recommended recipes
        recipes = Recipe.objects.filter(
            is_active=True,
            microbiome_score__gte=75
        ).order_by('-microbiome_score')[:3]
        
        # Substitutions
        substitutions = FoodSubstitution.objects.select_related(
            'food_to_avoid', 'food_to_prefer'
        ).order_by('-impact_score')[:3]
        
        # Seasonal foods
        current_month = datetime.now().month
        seasonal = SeasonalCalendar.objects.filter(
            region='Dakar',
            month=current_month,
            is_in_season=True
        ).select_related('food')[:4]
        
        return Response({
            'superfoods': SuperfoodSerializer(superfoods, many=True).data,
            'foods_to_avoid': FoodToAvoidSerializer(foods_to_avoid, many=True).data,
            'recommended_recipes': RecipeListSerializer(recipes, many=True).data,
            'substitutions': FoodSubstitutionSerializer(substitutions, many=True).data,
            'seasonal_foods': SeasonalCalendarSerializer(seasonal, many=True).data,
        })


# Data initialization view (for demo)
class InitializeNutritionDataView(APIView):
    """Initialize sample nutrition data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Create sample foods
        foods_data = [
            {
                'name': 'Fonio',
                'name_local': 'Fonio',
                'category': 'grain',
                'description': 'Riche en méthionine, facilite la digestion. Céréale ancienne africaine.',
                'prebiotic_score': 85,
                'fiber': 8.0,
                'icon': '🌾'
            },
            {
                'name': 'Fruit du Baobab',
                'name_local': 'Bouye',
                'category': 'superfood',
                'description': 'Prébiotique naturel puissant. Riche en vitamine C et fibres.',
                'prebiotic_score': 95,
                'fiber': 44.0,
                'icon': '🌳'
            },
            {
                'name': 'Arachides locales',
                'name_local': 'Tigal',
                'category': 'protein',
                'description': 'Source de protéines et de fibres. Bon pour la flore intestinale.',
                'prebiotic_score': 70,
                'fiber': 8.5,
                'icon': '🥜'
            },
            {
                'name': 'Lait caillé fermenté',
                'name_local': 'Thiakry',
                'category': 'fermented',
                'description': 'Naturellement riche en probiotiques. Excellent pour la digestion.',
                'prebiotic_score': 90,
                'probiotic': True,
                'icon': '🥛'
            },
            {
                'name': 'Pain de Singe',
                'name_local': 'Madd',
                'category': 'superfood',
                'description': 'Fruit riche en fibres et calcium. Prébiotique naturel.',
                'prebiotic_score': 80,
                'fiber': 10.0,
                'icon': '🍞'
            },
            {
                'name': 'Huile de Palme',
                'name_local': 'Touloucouna',
                'category': 'oil',
                'description': 'À consommer avec modération.',
                'prebiotic_score': 20,
                'anti_inflammatory': False,
                'icon': '🫒'
            },
            {
                'name': 'Huile de Coco',
                'name_local': 'Coco',
                'category': 'oil',
                'description': 'Alternative plus saine. Anti-inflammatoire.',
                'prebiotic_score': 60,
                'anti_inflammatory': True,
                'icon': '🥥'
            },
            {
                'name': 'Riz Blanc',
                'name_local': 'Riz',
                'category': 'grain',
                'description': 'Pauvre en fibres. Préférer le riz brun ou le fonio.',
                'prebiotic_score': 30,
                'fiber': 1.0,
                'icon': '🍚'
            },
            {
                'name': 'Mangue',
                'name_local': 'Mangué',
                'category': 'fruit',
                'description': 'Fruit de saison, riche en fibres et vitamines.',
                'prebiotic_score': 75,
                'fiber': 2.0,
                'season': 'dry',
                'icon': '🥭'
            },
            {
                'name': 'Ditakh',
                'name_local': 'Ditakh',
                'category': 'fruit',
                'description': 'Fruit local riche en vitamine C.',
                'prebiotic_score': 70,
                'fiber': 3.0,
                'season': 'rainy',
                'icon': '🍈'
            },
        ]
        
        created_foods = []
        for food_data in foods_data:
            food, created = FoodItem.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                created_foods.append(food.name)
        
        # Create sample recipes
        recipes_data = [
            {
                'name': 'Thieboudienne au riz brun et légumes',
                'description': 'Version saine du plat national sénégalais',
                'prep_time': 30,
                'cook_time': 45,
                'difficulty': 'medium',
                'microbiome_score': 85,
                'tags': ['traditionnel', 'riche-en-fibres'],
            },
            {
                'name': 'Bouillie de Mil fermentée',
                'description': 'Petit-déjeuner traditionnel riche en probiotiques',
                'prep_time': 10,
                'cook_time': 20,
                'difficulty': 'easy',
                'microbiome_score': 90,
                'tags': ['petit-dejeuner', 'fermenté'],
            },
        ]
        
        created_recipes = []
        for recipe_data in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data['name'],
                defaults=recipe_data
            )
            if created:
                created_recipes.append(recipe.name)
        
        # Create sample substitutions
        substitutions_data = [
            {'avoid': 'Riz Blanc', 'prefer': 'Fonio', 'impact': 42},
            {'avoid': 'Huile de Palme', 'prefer': 'Huile de Coco', 'impact': 35},
        ]
        
        created_subs = []
        for sub_data in substitutions_data:
            try:
                avoid = FoodItem.objects.get(name=sub_data['avoid'])
                prefer = FoodItem.objects.get(name=sub_data['prefer'])
                sub, created = FoodSubstitution.objects.get_or_create(
                    food_to_avoid=avoid,
                    food_to_prefer=prefer,
                    defaults={
                        'impact_score': sub_data['impact'],
                        'reason': f'Préférez {prefer.name} pour un meilleur équilibre intestinal.'
                    }
                )
                if created:
                    created_subs.append(f"{avoid.name} → {prefer.name}")
            except FoodItem.DoesNotExist:
                pass
        
        return Response({
            'message': 'Données nutritionnelles initialisées',
            'foods_created': created_foods,
            'recipes_created': created_recipes,
            'substitutions_created': created_subs
        })
