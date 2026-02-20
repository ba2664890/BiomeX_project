from rest_framework import serializers

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


class SiteMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteMetric
        fields = ["id", "key", "label", "value", "unit", "description"]


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ["key", "value", "description"]


class PricingPlanSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()
    price_fcfa_display = serializers.SerializerMethodField()

    class Meta:
        model = PricingPlan
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price_usd",
            "price_fcfa",
            "price_display",
            "price_fcfa_display",
            "features",
            "is_popular",
        ]

    def get_price_display(self, obj):
        return f"{int(obj.price_usd)}$"

    def get_price_fcfa_display(self, obj):
        return f"{obj.price_fcfa:,} FCFA".replace(",", " ")


class BlogArticleListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = BlogArticle
        fields = [
            "id",
            "category",
            "category_display",
            "title",
            "slug",
            "excerpt",
            "image_url",
            "published_at",
        ]


class BlogArticleDetailSerializer(BlogArticleListSerializer):
    class Meta(BlogArticleListSerializer.Meta):
        fields = BlogArticleListSerializer.Meta.fields + ["content", "is_featured"]


class FAQEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQEntry
        fields = ["id", "category", "question", "answer"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "full_name",
            "role",
            "company",
            "quote",
            "rating",
            "avatar_url",
            "location",
        ]


class NewsletterSubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ["id", "email", "full_name", "source"]


class KitOrderRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitOrderRequest
        fields = [
            "id",
            "plan",
            "full_name",
            "email",
            "phone",
            "city",
            "country",
            "message",
            "metadata",
        ]


class ContactRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = ["id", "full_name", "email", "phone", "company", "subject", "message"]
