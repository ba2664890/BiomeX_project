from django.urls import path
from .views import (
    UserRecommendationsView,
    RecommendationDetailView,
    MarkRecommendationReadView,
    MarkRecommendationCompletedView,
    DailyRecommendationsView,
    TodaysRecommendationsView,
    CreateSampleRecommendationsView,
    RAGHealthStatusView,
    RAGIngestKnowledgeView,
    RAGChatbotView,
)

urlpatterns = [
    path('', UserRecommendationsView.as_view(), name='user-recommendations'),
    path('<int:pk>/', RecommendationDetailView.as_view(), name='recommendation-detail'),
    path('<int:pk>/read/', MarkRecommendationReadView.as_view(), name='mark-recommendation-read'),
    path('<int:pk>/complete/', MarkRecommendationCompletedView.as_view(), name='mark-recommendation-complete'),
    path('daily/', DailyRecommendationsView.as_view(), name='daily-recommendations'),
    path('today/', TodaysRecommendationsView.as_view(), name='todays-recommendations'),
    path('create-sample/', CreateSampleRecommendationsView.as_view(), name='create-sample-recommendations'),
    path('rag/status/', RAGHealthStatusView.as_view(), name='rag-health-status'),
    path('rag/ingest/', RAGIngestKnowledgeView.as_view(), name='rag-ingest-knowledge'),
    path('rag/chat/', RAGChatbotView.as_view(), name='rag-chatbot'),
]
