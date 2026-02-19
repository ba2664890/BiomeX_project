from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'first_name', 'last_name', 'phone', 
        'is_premium', 'city', 'country', 'created_at'
    ]
    list_filter = ['is_premium', 'gender', 'country', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations personnelles', {
            'fields': ('phone', 'date_of_birth', 'gender', 'height', 'weight')
        }),
        ('Localisation', {
            'fields': ('city', 'country')
        }),
        ('Préférences', {
            'fields': ('dietary_preferences', 'allergies')
        }),
        ('Abonnement', {
            'fields': ('is_premium', 'premium_expiry')
        }),
        ('Confidentialité', {
            'fields': ('share_with_doctor', 'doctor_name', 'participate_in_research')
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'activity_type', 'is_read', 'created_at']
    list_filter = ['activity_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    ordering = ['-created_at']
