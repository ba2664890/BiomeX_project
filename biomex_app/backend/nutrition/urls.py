from django.urls import path
from .views import (
    FoodSearchView,
    FoodDetailView,
    SuperfoodsView,
    FoodsToAvoidView,
    RecipeListView,
    RecipeDetailView,
    RecommendedRecipesView,
    FoodSubstitutionsView,
    SeasonalCalendarView,
    NutritionDashboardView,
    InitializeNutritionDataView,
)

urlpatterns = [
    path('search/', FoodSearchView.as_view(), name='food-search'),
    path('foods/<int:pk>/', FoodDetailView.as_view(), name='food-detail'),
    path('superfoods/', SuperfoodsView.as_view(), name='superfoods'),
    path('foods-to-avoid/', FoodsToAvoidView.as_view(), name='foods-to-avoid'),
    path('recipes/', RecipeListView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipes/recommended/', RecommendedRecipesView.as_view(), name='recommended-recipes'),
    path('substitutions/', FoodSubstitutionsView.as_view(), name='food-substitutions'),
    path('seasonal/', SeasonalCalendarView.as_view(), name='seasonal-calendar'),
    path('dashboard/', NutritionDashboardView.as_view(), name='nutrition-dashboard'),
    path('initialize-data/', InitializeNutritionDataView.as_view(), name='initialize-nutrition-data'),
]
