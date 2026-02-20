from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(_("cree le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mis a jour le"), auto_now=True)

    class Meta:
        abstract = True


class SiteSetting(TimestampedModel):
    key = models.SlugField(_("cle"), max_length=100, unique=True)
    value = models.TextField(_("valeur"), blank=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    is_public = models.BooleanField(_("public"), default=True)

    class Meta:
        verbose_name = _("Parametre du site")
        verbose_name_plural = _("Parametres du site")
        ordering = ["key"]

    def __str__(self):
        return self.key


class SiteMetric(TimestampedModel):
    key = models.SlugField(_("cle"), max_length=100, unique=True)
    label = models.CharField(_("libelle"), max_length=120)
    value = models.CharField(_("valeur"), max_length=120)
    unit = models.CharField(_("unite"), max_length=30, blank=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    display_order = models.PositiveIntegerField(_("ordre d affichage"), default=0)
    is_active = models.BooleanField(_("actif"), default=True)

    class Meta:
        verbose_name = _("Metrique du site")
        verbose_name_plural = _("Metriques du site")
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"


class PricingPlan(TimestampedModel):
    name = models.CharField(_("nom"), max_length=120)
    slug = models.SlugField(_("slug"), max_length=140, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    price_usd = models.DecimalField(_("prix USD"), max_digits=10, decimal_places=2)
    price_fcfa = models.PositiveIntegerField(_("prix FCFA"))
    features = models.JSONField(_("fonctionnalites"), default=list, blank=True)
    is_popular = models.BooleanField(_("populaire"), default=False)
    is_active = models.BooleanField(_("actif"), default=True)
    display_order = models.PositiveIntegerField(_("ordre d affichage"), default=0)

    class Meta:
        verbose_name = _("Plan tarifaire")
        verbose_name_plural = _("Plans tarifaires")
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogArticle(TimestampedModel):
    CATEGORY_CHOICES = [
        ("science", _("Science")),
        ("nutrition", _("Nutrition")),
        ("research", _("Recherche")),
        ("tech", _("Technologie")),
        ("news", _("Actualite")),
    ]

    title = models.CharField(_("titre"), max_length=180)
    slug = models.SlugField(_("slug"), max_length=200, unique=True, blank=True)
    category = models.CharField(
        _("categorie"),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="science",
    )
    excerpt = models.TextField(_("resume"))
    content = models.TextField(_("contenu"), blank=True)
    image_url = models.URLField(_("image"), blank=True)
    is_published = models.BooleanField(_("publie"), default=True)
    is_featured = models.BooleanField(_("mis en avant"), default=False)
    published_at = models.DateTimeField(_("publie le"), null=True, blank=True)
    display_order = models.PositiveIntegerField(_("ordre d affichage"), default=0)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["display_order", "-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class FAQEntry(TimestampedModel):
    question = models.CharField(_("question"), max_length=255)
    answer = models.TextField(_("reponse"))
    category = models.CharField(_("categorie"), max_length=80, blank=True)
    is_active = models.BooleanField(_("actif"), default=True)
    display_order = models.PositiveIntegerField(_("ordre d affichage"), default=0)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.question


class Testimonial(TimestampedModel):
    full_name = models.CharField(_("nom"), max_length=120)
    role = models.CharField(_("role"), max_length=120, blank=True)
    company = models.CharField(_("organisation"), max_length=120, blank=True)
    quote = models.TextField(_("temoignage"))
    rating = models.PositiveSmallIntegerField(
        _("note"),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    avatar_url = models.URLField(_("avatar"), blank=True)
    location = models.CharField(_("ville"), max_length=120, blank=True)
    is_active = models.BooleanField(_("actif"), default=True)
    display_order = models.PositiveIntegerField(_("ordre d affichage"), default=0)

    class Meta:
        verbose_name = _("Temoignage")
        verbose_name_plural = _("Temoignages")
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.full_name


class NewsletterSubscription(TimestampedModel):
    email = models.EmailField(_("email"), unique=True)
    full_name = models.CharField(_("nom complet"), max_length=120, blank=True)
    source = models.CharField(_("source"), max_length=80, blank=True)
    is_active = models.BooleanField(_("actif"), default=True)

    class Meta:
        verbose_name = _("Inscription newsletter")
        verbose_name_plural = _("Inscriptions newsletter")
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class KitOrderRequest(TimestampedModel):
    STATUS_CHOICES = [
        ("new", _("Nouveau")),
        ("contacted", _("Contacte")),
        ("processing", _("En cours")),
        ("completed", _("Complete")),
        ("cancelled", _("Annule")),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("orange_money", _("Orange Money")),
        ("wave", _("Wave")),
        ("mtn_momo", _("MTN Mobile Money")),
        ("moov_money", _("Moov Money")),
        ("card", _("Carte bancaire")),
        ("bank_transfer", _("Virement bancaire")),
        ("cash_on_delivery", _("Paiement a la livraison")),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", _("En attente")),
        ("proof_submitted", _("Preuve soumise")),
        ("verified", _("Verifie")),
        ("rejected", _("Rejete")),
        ("manual_review", _("Revision manuelle")),
    ]

    plan = models.CharField(_("plan"), max_length=120)
    full_name = models.CharField(_("nom complet"), max_length=120)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("telephone"), max_length=40, blank=True)
    city = models.CharField(_("ville"), max_length=120, blank=True)
    country = models.CharField(_("pays"), max_length=120, default="Senegal", blank=True)
    quantity = models.PositiveSmallIntegerField(_("quantite"), default=1)
    unit_price_fcfa = models.PositiveIntegerField(_("prix unitaire FCFA"), default=0)
    amount_total_fcfa = models.PositiveIntegerField(_("montant total FCFA"), default=0)
    currency = models.CharField(_("devise"), max_length=8, default="XOF")
    payment_method = models.CharField(
        _("methode de paiement"),
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="orange_money",
    )
    payment_provider = models.CharField(_("operateur paiement"), max_length=80, blank=True)
    payment_phone = models.CharField(_("telephone paiement"), max_length=40, blank=True)
    payment_reference = models.CharField(_("reference paiement"), max_length=120, blank=True)
    payment_last4 = models.CharField(_("4 derniers chiffres carte"), max_length=4, blank=True)
    payment_status = models.CharField(
        _("statut paiement"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    payment_verified = models.BooleanField(_("paiement verifie"), default=False)
    payment_verified_at = models.DateTimeField(_("paiement verifie le"), null=True, blank=True)
    payment_verification_notes = models.TextField(_("notes verification paiement"), blank=True)
    accepted_terms = models.BooleanField(_("conditions acceptees"), default=False)
    source = models.CharField(_("source"), max_length=80, default="site_app", blank=True)
    client_ip = models.GenericIPAddressField(_("ip client"), null=True, blank=True)
    user_agent = models.CharField(_("user agent"), max_length=255, blank=True)
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    geolocation_accuracy_meters = models.FloatField(
        _("precision geolocalisation (m)"),
        null=True,
        blank=True,
    )
    geolocation_source = models.CharField(
        _("source geolocalisation"),
        max_length=40,
        default="browser_gps",
        blank=True,
    )
    geolocation_captured_at = models.DateTimeField(
        _("geolocalisation capturee le"),
        null=True,
        blank=True,
    )
    verification_flags = models.JSONField(_("flags verification"), default=list, blank=True)
    message = models.TextField(_("message"), blank=True)
    status = models.CharField(
        _("statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )
    sample_id = models.CharField(_("id echantillon"), max_length=80, blank=True)
    estimated_delivery = models.DateField(_("livraison estimee"), null=True, blank=True)
    metadata = models.JSONField(_("metadonnees"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Demande kit")
        verbose_name_plural = _("Demandes kits")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.plan} - {self.full_name}"


class ContactRequest(TimestampedModel):
    STATUS_CHOICES = [
        ("new", _("Nouveau")),
        ("in_progress", _("En cours")),
        ("resolved", _("Traite")),
    ]

    full_name = models.CharField(_("nom complet"), max_length=120)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("telephone"), max_length=40, blank=True)
    company = models.CharField(_("societe"), max_length=120, blank=True)
    subject = models.CharField(_("sujet"), max_length=180)
    message = models.TextField(_("message"))
    status = models.CharField(
        _("statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    class Meta:
        verbose_name = _("Demande de contact")
        verbose_name_plural = _("Demandes de contact")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
