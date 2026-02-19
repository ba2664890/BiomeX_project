from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Recommendation(models.Model):
    """Personalized recommendations for users"""
    
    CATEGORY_CHOICES = [
        ('food', _('Alimentation')),
        ('lifestyle', _('Mode de vie')),
        ('supplement', _('Supplément')),
        ('exercise', _('Exercice')),
        ('sleep', _('Sommeil')),
        ('hydration', _('Hydratation')),
    ]
    
    PRIORITY_CHOICES = [
        ('high', _('Haute')),
        ('medium', _('Moyenne')),
        ('low', _('Basse')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(_('priorité'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Related entities
    related_food = models.ForeignKey(
        'nutrition.FoodItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendations'
    )
    related_recipe = models.ForeignKey(
        'nutrition.Recipe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendations'
    )
    
    # Impact
    expected_score_improvement = models.IntegerField(_('amélioration attendue'), default=0)
    
    # Status
    is_read = models.BooleanField(_('lu'), default=False)
    is_completed = models.BooleanField(_('complété'), default=False)
    completed_at = models.DateTimeField(_('complété le'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expire le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Recommandation')
        verbose_name_plural = _('Recommandations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class DailyRecommendation(models.Model):
    """Daily recommendations that apply to all users"""
    
    CATEGORY_CHOICES = [
        ('food', _('Alimentation')),
        ('lifestyle', _('Mode de vie')),
        ('supplement', _('Supplément')),
        ('exercise', _('Exercice')),
        ('sleep', _('Sommeil')),
        ('hydration', _('Hydratation')),
    ]
    
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    
    # Related food or recipe
    related_food = models.ForeignKey(
        'nutrition.FoodItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Icon/image
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    
    # Active period
    is_active = models.BooleanField(_('actif'), default=True)
    start_date = models.DateField(_('date de début'), null=True, blank=True)
    end_date = models.DateField(_('date de fin'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Recommandation Quotidienne')
        verbose_name_plural = _('Recommandations Quotidiennes')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
