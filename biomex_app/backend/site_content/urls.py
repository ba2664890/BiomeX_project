from django.urls import path

from .views import (
    BlogArticleDetailView,
    BlogArticlesView,
    ContactRequestCreateView,
    FAQListView,
    HomeContentView,
    KitOrderCreateView,
    NewsletterSubscribeView,
    PricingPlansView,
    SiteMetricsView,
    TestimonialListView,
)

urlpatterns = [
    path("home/", HomeContentView.as_view(), name="site-home-content"),
    path("newsletter/", NewsletterSubscribeView.as_view(), name="site-newsletter-subscribe"),
    path("kit-orders/", KitOrderCreateView.as_view(), name="site-kit-order-create"),
    path("contact-requests/", ContactRequestCreateView.as_view(), name="site-contact-request-create"),
    path("pricing/", PricingPlansView.as_view(), name="site-pricing-list"),
    path("blog/", BlogArticlesView.as_view(), name="site-blog-list"),
    path("blog/<slug:slug>/", BlogArticleDetailView.as_view(), name="site-blog-detail"),
    path("faqs/", FAQListView.as_view(), name="site-faq-list"),
    path("testimonials/", TestimonialListView.as_view(), name="site-testimonial-list"),
    path("metrics/", SiteMetricsView.as_view(), name="site-metric-list"),
]
