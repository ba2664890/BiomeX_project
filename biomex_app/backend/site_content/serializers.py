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
    PLAN_PRICE_FCFA = {
        "kit standard": 75000,
        "kit premium": 120000,
    }

    MOBILE_PAYMENT_METHODS = {"orange_money", "wave", "mtn_momo", "moov_money"}

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
            "quantity",
            "unit_price_fcfa",
            "amount_total_fcfa",
            "currency",
            "payment_method",
            "payment_provider",
            "payment_phone",
            "payment_reference",
            "payment_last4",
            "accepted_terms",
            "source",
            "latitude",
            "longitude",
            "geolocation_accuracy_meters",
            "geolocation_source",
            "payment_status",
            "payment_verification_notes",
            "verification_flags",
            "message",
            "metadata",
        ]

    def validate(self, attrs):
        plan = (attrs.get("plan") or "").strip()
        plan_key = plan.lower()
        full_name = (attrs.get("full_name") or "").strip()
        email = (attrs.get("email") or "").strip().lower()
        phone = (attrs.get("phone") or "").strip()
        payment_phone = (attrs.get("payment_phone") or "").strip()
        payment_reference = (attrs.get("payment_reference") or "").strip()
        payment_last4 = (attrs.get("payment_last4") or "").strip()
        payment_method = attrs.get("payment_method") or "orange_money"
        try:
            quantity = int(attrs.get("quantity") or 1)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"quantity": "La quantite est invalide."})
        source = (attrs.get("source") or "site_app").strip()
        payment_provider = (attrs.get("payment_provider") or payment_method).strip()
        currency = (attrs.get("currency") or "XOF").strip().upper()
        geolocation_source = (attrs.get("geolocation_source") or "browser_gps").strip()[:40]
        try:
            unit_price_fcfa = int(attrs.get("unit_price_fcfa") or 0)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"unit_price_fcfa": "Le prix unitaire est invalide."})
        try:
            amount_total_fcfa = int(attrs.get("amount_total_fcfa") or 0)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"amount_total_fcfa": "Le montant total est invalide."})
        try:
            latitude = float(attrs.get("latitude"))
            longitude = float(attrs.get("longitude"))
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {"latitude": "La localisation exacte (latitude/longitude) est obligatoire."}
            )

        geolocation_accuracy_meters = attrs.get("geolocation_accuracy_meters")
        if geolocation_accuracy_meters is not None:
            try:
                geolocation_accuracy_meters = float(geolocation_accuracy_meters)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {"geolocation_accuracy_meters": "La precision GPS est invalide."}
                )

        if not full_name:
            raise serializers.ValidationError({"full_name": "Le nom complet est obligatoire."})

        if not email and not phone:
            raise serializers.ValidationError(
                {"phone": "Merci de fournir au moins un email ou un numero de telephone."}
            )

        if quantity < 1 or quantity > 20:
            raise serializers.ValidationError({"quantity": "La quantite doit etre entre 1 et 20."})

        if attrs.get("accepted_terms") is not True:
            raise serializers.ValidationError(
                {"accepted_terms": "Vous devez accepter les conditions d'achat."}
            )

        if not plan:
            raise serializers.ValidationError({"plan": "Le plan est obligatoire."})

        if latitude < -90 or latitude > 90:
            raise serializers.ValidationError({"latitude": "Latitude invalide."})

        if longitude < -180 or longitude > 180:
            raise serializers.ValidationError({"longitude": "Longitude invalide."})

        if geolocation_accuracy_meters is not None and geolocation_accuracy_meters <= 0:
            raise serializers.ValidationError(
                {"geolocation_accuracy_meters": "La precision GPS doit etre positive."}
            )

        if payment_method in self.MOBILE_PAYMENT_METHODS and not payment_phone:
            raise serializers.ValidationError(
                {"payment_phone": "Le telephone de paiement est obligatoire pour Mobile Money."}
            )

        if payment_method != "cash_on_delivery" and not payment_reference:
            raise serializers.ValidationError(
                {
                    "payment_reference": "La reference de paiement est obligatoire pour valider la commande."
                }
            )

        if payment_method == "card" and (not payment_last4.isdigit() or len(payment_last4) != 4):
            raise serializers.ValidationError(
                {"payment_last4": "Merci d'indiquer les 4 derniers chiffres de la carte."}
            )

        expected_unit_price = self.PLAN_PRICE_FCFA.get(plan_key)
        if expected_unit_price is None and unit_price_fcfa <= 0:
            raise serializers.ValidationError(
                {"unit_price_fcfa": "Prix unitaire introuvable pour ce plan."}
            )
        if expected_unit_price is None:
            expected_unit_price = unit_price_fcfa

        expected_total = expected_unit_price * quantity
        provided_total = amount_total_fcfa or expected_total

        verification_flags = []
        payment_status = "proof_submitted" if payment_reference else "pending"
        payment_verification_notes = ""

        if provided_total != expected_total:
            verification_flags.append("amount_mismatch")
            payment_status = "manual_review"
            payment_verification_notes = (
                f"Montant recu {provided_total} FCFA, attendu {expected_total} FCFA."
            )

        if payment_method == "cash_on_delivery":
            payment_status = "pending"

        if geolocation_accuracy_meters is not None and geolocation_accuracy_meters > 150:
            verification_flags.append("low_location_accuracy")
            if payment_status != "manual_review":
                payment_status = "manual_review"
            if not payment_verification_notes:
                payment_verification_notes = (
                    f"Precision GPS faible ({geolocation_accuracy_meters:.0f} m)."
                )

        attrs["plan"] = plan
        attrs["full_name"] = full_name
        attrs["email"] = email
        attrs["phone"] = phone
        attrs["payment_phone"] = payment_phone
        attrs["payment_reference"] = payment_reference
        attrs["payment_last4"] = payment_last4
        attrs["quantity"] = quantity
        attrs["unit_price_fcfa"] = expected_unit_price
        attrs["amount_total_fcfa"] = provided_total
        attrs["currency"] = currency
        attrs["source"] = source
        attrs["payment_provider"] = payment_provider
        attrs["latitude"] = round(latitude, 6)
        attrs["longitude"] = round(longitude, 6)
        attrs["geolocation_accuracy_meters"] = geolocation_accuracy_meters
        attrs["geolocation_source"] = geolocation_source
        attrs["payment_status"] = payment_status
        attrs["payment_verification_notes"] = payment_verification_notes
        attrs["verification_flags"] = verification_flags
        return attrs


class ContactRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = ["id", "full_name", "email", "phone", "company", "subject", "message"]
