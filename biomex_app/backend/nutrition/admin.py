from django.contrib import admin
from .models import FoodItem, Recipe, RecipeIngredient, FoodSubstitution, SeasonalCalendar


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'prebiotic_score', 'probiotic',
        'anti_inflammatory', 'is_active'
    ]
    list_filter = ['category', 'probiotic', 'anti_inflammatory', 'is_active']
    search_fields = ['name', 'name_local', 'description']
    ordering = ['name']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'prep_time', 'cook_time', 'difficulty', 'microbiome_score', 'is_active']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['name', 'description']
    inlines = [RecipeIngredientInline]


@admin.register(FoodSubstitution)
class FoodSubstitutionAdmin(admin.ModelAdmin):
    list_display = ['food_to_avoid', 'food_to_prefer', 'impact_score']
    search_fields = ['food_to_avoid__name', 'food_to_prefer__name']


@admin.register(SeasonalCalendar)
class SeasonalCalendarAdmin(admin.ModelAdmin):
    list_display = ['food', 'month', 'region', 'is_in_season']
    list_filter = ['month', 'region', 'is_in_season']
