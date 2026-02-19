from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class DailyWellnessCheck(models.Model):
    """Daily wellness check-in from user"""
    
    CATEGORY_CHOICES = [
        ('digestive', _('Digestif')),
        ('energy', _('Énergie')),
        ('sleep', _('Sommeil')),
        ('skin', _('Peau')),
        ('mood', _('Humeur')),
        ('stress', _('Stress')),
    ]
    
    RATING_CHOICES = [
        (1, _('Mauvais')),
        (2, _('Faible')),
        (3, _('Moyen')),
        (4, _('Bon')),
        (5, _('Excellent')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wellness_checks'
    )
    date = models.DateField(_('date'))
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    rating = models.IntegerField(_('note'), choices=RATING_CHOICES)
    notes = models.TextField(_('notes'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Bilan Quotidien')
        verbose_name_plural = _('Bilans Quotidiens')
        unique_together = ['user', 'date', 'category']
        ordering = ['-date', 'category']
    
    def __str__(self):
        return f"{self.user.email} - {self.category} ({self.date}): {self.rating}/5"


class HealthMetric(models.Model):
    """Track various health metrics over time"""
    
    METRIC_CHOICES = [
        ('weight', _('Poids')),
        ('bmi', _('IMC')),
        ('waist', _('Tour de taille')),
        ('blood_pressure_systolic', _('Tension artérielle (systolique)')),
        ('blood_pressure_diastolic', _('Tension artérielle (diastolique)')),
        ('blood_glucose', _('Glycémie')),
        ('heart_rate', _('Fréquence cardiaque')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    metric_type = models.CharField(_('type'), max_length=30, choices=METRIC_CHOICES)
    value = models.FloatField(_('valeur'))
    unit = models.CharField(_('unité'), max_length=20, blank=True)
    date = models.DateField(_('date'))
    notes = models.TextField(_('notes'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Métrique de Santé')
        verbose_name_plural = _('Métriques de Santé')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.metric_type}: {self.value} {self.unit}"


class SymptomLog(models.Model):
    """Log symptoms for tracking"""
    
    SEVERITY_CHOICES = [
        ('mild', _('Léger')),
        ('moderate', _('Modéré')),
        ('severe', _('Sévère')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='symptom_logs'
    )
    symptom = models.CharField(_('symptôme'), max_length=200)
    severity = models.CharField(_('gravité'), max_length=20, choices=SEVERITY_CHOICES)
    date = models.DateField(_('date'))
    duration_hours = models.IntegerField(_('durée (heures)'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Journal de Symptômes')
        verbose_name_plural = _('Journaux de Symptômes')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.symptom} ({self.date})"


class WeeklyInsight(models.Model):
    """Weekly insights generated from user data"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='weekly_insights'
    )
    week_start = models.DateField(_('début de semaine'))
    week_end = models.DateField(_('fin de semaine'))
    
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    insight_type = models.CharField(_('type'), max_length=50, default='general')
    
    # Related metrics
    related_food = models.CharField(_('aliment lié'), max_length=200, blank=True)
    score_change = models.IntegerField(_('changement de score'), default=0)
    
    is_read = models.BooleanField(_('lu'), default=False)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Insight Hebdomadaire')
        verbose_name_plural = _('Insights Hebdomadaires')
        ordering = ['-week_start']
    
    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.week_start})"


class Routine(models.Model):
    """User's daily routines and habits"""
    
    ROUTINE_TYPE_CHOICES = [
        ('morning', _('Matin')),
        ('meal', _('Repas')),
        ('evening', _('Soir')),
        ('exercise', _('Exercice')),
        ('supplement', _('Supplément')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='routines'
    )
    name = models.CharField(_('nom'), max_length=200)
    routine_type = models.CharField(_('type'), max_length=20, choices=ROUTINE_TYPE_CHOICES)
    description = models.TextField(_('description'), blank=True)
    time_of_day = models.TimeField(_('heure'), null=True, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Routine')
        verbose_name_plural = _('Routines')
        ordering = ['time_of_day']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class RoutineLog(models.Model):
    """Log when user completes a routine"""
    routine = models.ForeignKey(
        Routine,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    date = models.DateField(_('date'))
    completed = models.BooleanField(_('complété'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Journal de Routine')
        verbose_name_plural = _('Journaux de Routines')
        unique_together = ['routine', 'date']
    
    def __str__(self):
        return f"{self.routine.name} - {self.date}: {'✓' if self.completed else '✗'}"
