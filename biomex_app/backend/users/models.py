from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', _('Masculin')),
        ('F', _('Féminin')),
        ('O', _('Autre')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    
    # Profile fields
    date_of_birth = models.DateField(_('date de naissance'), null=True, blank=True)
    gender = models.CharField(_('genre'), max_length=1, choices=GENDER_CHOICES, blank=True)
    height = models.FloatField(_('taille (cm)'), null=True, blank=True)
    weight = models.FloatField(_('poids (kg)'), null=True, blank=True)
    
    # Location
    city = models.CharField(_('ville'), max_length=100, blank=True)
    country = models.CharField(_('pays'), max_length=100, blank=True, default='Sénégal')
    
    # Preferences
    dietary_preferences = models.JSONField(_('préférences alimentaires'), default=list, blank=True)
    allergies = models.JSONField(_('allergies'), default=list, blank=True)
    
    # Subscription
    is_premium = models.BooleanField(_('premium'), default=False)
    premium_expiry = models.DateTimeField(_('expiration premium'), null=True, blank=True)
    
    # Privacy settings
    share_with_doctor = models.BooleanField(_('partager avec médecin'), default=False)
    doctor_name = models.CharField(_('nom du médecin'), max_length=200, blank=True)
    participate_in_research = models.BooleanField(_('participer à la recherche'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None


class UserActivity(models.Model):
    """Track user activities and notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    activity_type = models.CharField(_('type'), max_length=50, default='general')
    is_read = models.BooleanField(_('lu'), default=False)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Activité utilisateur')
        verbose_name_plural = _('Activités utilisateurs')
        ordering = ['-created_at']
