from django.contrib import admin

from .models import (
    BlogArticle,
    ContactRequest,
    FAQEntry,
    KitOrderRequest,
    NewsletterSubscription,
    PricingPlan,
    SiteMetric,
    SiteSetting,
    Testimonial,
)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "is_public", "updated_at")
    list_filter = ("is_public",)
    search_fields = ("key", "description")


@admin.register(SiteMetric)
class SiteMetricAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "value", "unit", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("key", "label")
    ordering = ("display_order", "id")


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_usd", "price_fcfa", "is_popular", "is_active", "display_order")
    list_filter = ("is_popular", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "id")


@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "is_featured", "published_at", "display_order")
    list_filter = ("category", "is_published", "is_featured")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("display_order", "-published_at", "-created_at")


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_active", "display_order")
    list_filter = ("is_active", "category")
    search_fields = ("question", "answer")
    ordering = ("display_order", "id")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "company", "rating", "is_active", "display_order")
    list_filter = ("is_active", "rating")
    search_fields = ("full_name", "role", "company", "quote")
    ordering = ("display_order", "id")


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "source", "is_active", "created_at")
    list_filter = ("is_active", "source")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)


@admin.register(KitOrderRequest)
class KitOrderRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "plan", "full_name", "email", "phone", "status", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("full_name", "email", "phone", "sample_id")
    ordering = ("-created_at",)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "subject", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "subject", "message")
    ordering = ("-created_at",)
