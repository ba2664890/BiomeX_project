from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class FoodItem(models.Model):
    """Food items database with nutritional information"""
    
    CATEGORY_CHOICES = [
        ('grain', _('Céréale')),
        ('vegetable', _('Légume')),
        ('fruit', _('Fruit')),
        ('protein', _('Protéine')),
        ('dairy', _('Produit laitier')),
        ('fermented', _('Fermenté')),
        ('oil', _('Huile')),
        ('spice', _('Épice')),
        ('superfood', _('Super-aliment')),
    ]
    
    SEASON_CHOICES = [
        ('all', _('Toute l\'année')),
        ('dry', _('Saison sèche')),
        ('rainy', _('Saison des pluies')),
    ]
    
    name = models.CharField(_('nom'), max_length=200)
    name_local = models.CharField(_('nom local'), max_length=200, blank=True)
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(_('description'), blank=True)
    
    # Nutritional info (per 100g)
    calories = models.FloatField(_('calories'), default=0)
    proteins = models.FloatField(_('protéines'), default=0)
    carbs = models.FloatField(_('glucides'), default=0)
    fats = models.FloatField(_('lipides'), default=0)
    fiber = models.FloatField(_('fibres'), default=0)
    
    # Microbiome impact
    prebiotic_score = models.IntegerField(_('score prébiotique'), default=50)
    probiotic = models.BooleanField(_('probiotique'), default=False)
    anti_inflammatory = models.BooleanField(_('anti-inflammatoire'), default=False)
    
    # Seasonality
    season = models.CharField(_('saison'), max_length=10, choices=SEASON_CHOICES, default='all')
    
    # Images
    image = models.ImageField(_('image'), upload_to='foods/', blank=True, null=True)
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    
    # Metadata
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Aliment')
        verbose_name_plural = _('Aliments')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipes with microbiome-friendly ingredients"""
    
    DIFFICULTY_CHOICES = [
        ('easy', _('Facile')),
        ('medium', _('Moyen')),
        ('hard', _('Difficile')),
    ]
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Recipe details
    prep_time = models.IntegerField(_('temps de préparation'), default=15)
    cook_time = models.IntegerField(_('temps de cuisson'), default=30)
    difficulty = models.CharField(_('difficulté'), max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    servings = models.IntegerField(_('portions'), default=4)
    
    # Ingredients
    ingredients = models.ManyToManyField(FoodItem, through='RecipeIngredient')
    
    # Instructions
    instructions = models.JSONField(_('instructions'), default=list)
    
    # Tags
    tags = models.JSONField(_('tags'), default=list, blank=True)
    
    # Images
    image = models.ImageField(_('image'), upload_to='recipes/', blank=True, null=True)
    
    # Scores
    microbiome_score = models.IntegerField(_('score microbiome'), default=70)
    
    # Metadata
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Recette')
        verbose_name_plural = _('Recettes')
        ordering = ['-microbiome_score', 'name']
    
    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Link between recipes and ingredients with quantities"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.CharField(_('quantité'), max_length=100)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Ingrédient de recette')
        verbose_name_plural = _('Ingrédients de recettes')
    
    def __str__(self):
        return f"{self.quantity} {self.food.name}"


class FoodSubstitution(models.Model):
    """Food substitution recommendations"""
    food_to_avoid = models.ForeignKey(
        FoodItem, 
        on_delete=models.CASCADE,
        related_name='substitutions_to_avoid'
    )
    food_to_prefer = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='substitutions_to_prefer'
    )
    impact_score = models.IntegerField(_('impact sur le score'), default=0)
    reason = models.TextField(_('raison'), blank=True)
    
    class Meta:
        verbose_name = _('Substitution alimentaire')
        verbose_name_plural = _('Substitutions alimentaires')
    
    def __str__(self):
        return f"{self.food_to_avoid.name} → {self.food_to_prefer.name}"


class SeasonalCalendar(models.Model):
    """Track seasonal availability of foods"""
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='seasonal_info')
    month = models.IntegerField(_('mois'))
    is_in_season = models.BooleanField(_('en saison'), default=True)
    region = models.CharField(_('région'), max_length=100, default='Dakar')
    
    class Meta:
        verbose_name = _('Calendrier saisonnier')
        verbose_name_plural = _('Calendriers saisonniers')
        unique_together = ['food', 'month', 'region']
    
    def __str__(self):
        return f"{self.food.name} - Mois {self.month} ({self.region})"
