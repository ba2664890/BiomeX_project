from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BlogArticle,
    FAQEntry,
    NewsletterSubscription,
    PricingPlan,
    SiteMetric,
    SiteSetting,
    Testimonial,
)
from .serializers import (
    BlogArticleDetailSerializer,
    BlogArticleListSerializer,
    ContactRequestCreateSerializer,
    FAQEntrySerializer,
    KitOrderRequestCreateSerializer,
    NewsletterSubscriptionCreateSerializer,
    PricingPlanSerializer,
    SiteMetricSerializer,
    SiteSettingSerializer,
    TestimonialSerializer,
)


class HomeContentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        metrics = SiteMetric.objects.filter(is_active=True).order_by("display_order", "id")
        latest_articles = BlogArticle.objects.filter(is_published=True).order_by(
            "display_order",
            "-published_at",
            "-created_at",
        )[:6]
        pricing_plans = PricingPlan.objects.filter(is_active=True).order_by(
            "display_order",
            "id",
        )
        faqs = FAQEntry.objects.filter(is_active=True).order_by("display_order", "id")[:8]
        testimonials = Testimonial.objects.filter(is_active=True).order_by(
            "display_order",
            "id",
        )[:6]
        settings_qs = SiteSetting.objects.filter(is_public=True).order_by("key")

        data = {
            "metrics": SiteMetricSerializer(metrics, many=True).data,
            "latest_articles": BlogArticleListSerializer(latest_articles, many=True).data,
            "pricing_plans": PricingPlanSerializer(pricing_plans, many=True).data,
            "faqs": FAQEntrySerializer(faqs, many=True).data,
            "testimonials": TestimonialSerializer(testimonials, many=True).data,
            "settings": SiteSettingSerializer(settings_qs, many=True).data,
        }

        return Response({"status": "ok", "data": data})


class PricingPlansView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        plans = PricingPlan.objects.filter(is_active=True).order_by("display_order", "id")
        return Response(
            {
                "status": "ok",
                "count": plans.count(),
                "data": PricingPlanSerializer(plans, many=True).data,
            }
        )


class BlogArticlesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        articles = BlogArticle.objects.filter(is_published=True).order_by(
            "display_order",
            "-published_at",
            "-created_at",
        )
        return Response(
            {
                "status": "ok",
                "count": articles.count(),
                "data": BlogArticleListSerializer(articles, many=True).data,
            }
        )


class BlogArticleDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        article = get_object_or_404(BlogArticle, slug=slug, is_published=True)
        return Response({"status": "ok", "data": BlogArticleDetailSerializer(article).data})


class FAQListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        faqs = FAQEntry.objects.filter(is_active=True).order_by("display_order", "id")
        return Response(
            {"status": "ok", "count": faqs.count(), "data": FAQEntrySerializer(faqs, many=True).data}
        )


class TestimonialListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        testimonials = Testimonial.objects.filter(is_active=True).order_by("display_order", "id")
        return Response(
            {
                "status": "ok",
                "count": testimonials.count(),
                "data": TestimonialSerializer(testimonials, many=True).data,
            }
        )


class SiteMetricsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        metrics = SiteMetric.objects.filter(is_active=True).order_by("display_order", "id")
        return Response(
            {
                "status": "ok",
                "count": metrics.count(),
                "data": SiteMetricSerializer(metrics, many=True).data,
            }
        )


class NewsletterSubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = NewsletterSubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip()
        full_name = serializer.validated_data.get("full_name", "").strip()
        source = serializer.validated_data.get("source", "").strip()

        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "source": source,
                "is_active": True,
            },
        )

        if not created:
            changed = False
            if full_name and subscription.full_name != full_name:
                subscription.full_name = full_name
                changed = True
            if source and subscription.source != source:
                subscription.source = source
                changed = True
            if not subscription.is_active:
                subscription.is_active = True
                changed = True
            if changed:
                subscription.save()

        return Response(
            {
                "status": "ok",
                "message": "Inscription newsletter enregistree.",
                "subscription_id": subscription.id,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class KitOrderCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = KitOrderRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
        user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]

        kit_order = serializer.save(
            client_ip=client_ip,
            user_agent=user_agent,
            geolocation_captured_at=timezone.now(),
        )

        response_payload = {
            "status": "ok",
            "message": "Demande de kit enregistree.",
            "request_id": kit_order.id,
            "payment_status": kit_order.payment_status,
            "verification_flags": kit_order.verification_flags,
            "payment_verification_notes": kit_order.payment_verification_notes,
            "location": {
                "latitude": kit_order.latitude,
                "longitude": kit_order.longitude,
                "accuracy_meters": kit_order.geolocation_accuracy_meters,
            },
        }

        if kit_order.sample_id:
            response_payload["sample_id"] = kit_order.sample_id
        if kit_order.estimated_delivery:
            response_payload["estimated_delivery"] = kit_order.estimated_delivery.isoformat()

        return Response(response_payload, status=status.HTTP_201_CREATED)


class ContactRequestCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_request = serializer.save()
        return Response(
            {
                "status": "ok",
                "message": "Demande de contact enregistree.",
                "request_id": contact_request.id,
            },
            status=status.HTTP_201_CREATED,
        )
