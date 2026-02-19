from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class MicrobiomeAnalysis(models.Model):
    """Main analysis result for a user's microbiome sample"""
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('processing', _('En traitement')),
        ('completed', _('Terminé')),
        ('failed', _('Échoué')),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='microbiome_analyses'
    )
    
    # Sample information
    sample_id = models.CharField(_('ID échantillon'), max_length=100, unique=True)
    sample_date = models.DateField(_('date de prélèvement'))
    
    # Analysis status
    status = models.CharField(
        _('statut'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Overall scores
    overall_score = models.IntegerField(_('score global'), default=0)
    diversity_score = models.IntegerField(_('score diversité'), default=0)
    inflammation_score = models.IntegerField(_('score inflammation'), default=0)
    gut_brain_score = models.IntegerField(_('score axe intestin-cerveau'), default=0)
    
    # Detailed metrics
    species_count = models.IntegerField(_('nombre d\'espèces'), default=0)
    probiotic_count = models.IntegerField(_('nombre de probiotiques'), default=0)
    pathogen_percentage = models.FloatField(_('pourcentage pathogènes'), default=0)
    
    # Diversity indices
    shannon_index = models.FloatField(_('indice de Shannon'), null=True, blank=True)
    simpson_index = models.FloatField(_('indice de Simpson'), null=True, blank=True)
    chao1_index = models.FloatField(_('indice Chao1'), null=True, blank=True)
    
    # Comparison data
    percentile_africa = models.IntegerField(_('percentile Afrique'), default=50)
    percentile_local = models.IntegerField(_('percentile local'), default=50)
    
    # Next test recommendation
    next_test_date = models.DateField(_('prochain test recommandé'), null=True, blank=True)
    
    # Analysis notes
    summary = models.TextField(_('résumé'), blank=True)
    recommendations = models.TextField(_('recommandations'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Analyse Microbiome')
        verbose_name_plural = _('Analyses Microbiome')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analyse {self.sample_id} - {self.user.email} ({self.overall_score}/100)"


class BacteriaBalance(models.Model):
    """Bacterial balance data for an analysis"""
    
    STATUS_CHOICES = [
        ('low', _('Faible')),
        ('optimal', _('Optimal')),
        ('elevated', _('Élevé')),
    ]
    
    analysis = models.ForeignKey(
        MicrobiomeAnalysis,
        on_delete=models.CASCADE,
        related_name='bacteria_balances'
    )
    
    bacteria_name = models.CharField(_('nom bactérie'), max_length=200)
    bacteria_type = models.CharField(_('type'), max_length=100, blank=True)
    percentage = models.FloatField(_('pourcentage'))
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES)
    reference_min = models.FloatField(_('référence min'), default=0)
    reference_max = models.FloatField(_('référence max'), default=100)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('Équilibre Bactérien')
        verbose_name_plural = _('Équilibres Bactériens')
        ordering = ['-percentage']
    
    def __str__(self):
        return f"{self.bacteria_name}: {self.percentage}% ({self.status})"


class HealthMarker(models.Model):
    """Health markers derived from microbiome analysis"""
    
    CATEGORY_CHOICES = [
        ('metabolic', _('Métabolique')),
        ('immune', _('Immunitaire')),
        ('digestive', _('Digestif')),
        ('mental', _('Mental')),
        ('cardiovascular', _('Cardiovasculaire')),
    ]
    
    analysis = models.ForeignKey(
        MicrobiomeAnalysis,
        on_delete=models.CASCADE,
        related_name='health_markers'
    )
    
    name = models.CharField(_('nom'), max_length=200)
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    score = models.IntegerField(_('score'))
    status = models.CharField(_('statut'), max_length=50)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('Marqueur de Santé')
        verbose_name_plural = _('Marqueurs de Santé')
    
    def __str__(self):
        return f"{self.name}: {self.score}/100"


class AnalysisHistory(models.Model):
    """Track score changes over time"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='score_history'
    )
    date = models.DateField(_('date'))
    overall_score = models.IntegerField(_('score global'))
    diversity_score = models.IntegerField(_('score diversité'))
    inflammation_score = models.IntegerField(_('score inflammation'))
    gut_brain_score = models.IntegerField(_('score axe intestin-cerveau'))
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Historique des Scores')
        verbose_name_plural = _('Historique des Scores')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.overall_score}/100"
