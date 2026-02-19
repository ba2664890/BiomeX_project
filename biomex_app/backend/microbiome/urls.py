from django.urls import path
from .views import (
    LatestAnalysisView,
    AnalysisDetailView,
    AnalysisListView,
    DashboardScoresView,
    BacteriaBalanceView,
    HealthMarkersView,
    ScoreHistoryView,
    RequestNewKitView,
    CreateSampleAnalysisView,
)

urlpatterns = [
    path('latest/', LatestAnalysisView.as_view(), name='latest-analysis'),
    path('list/', AnalysisListView.as_view(), name='analysis-list'),
    path('detail/<int:pk>/', AnalysisDetailView.as_view(), name='analysis-detail'),
    path('dashboard-scores/', DashboardScoresView.as_view(), name='dashboard-scores'),
    path('bacteria-balance/', BacteriaBalanceView.as_view(), name='bacteria-balance'),
    path('bacteria-balance/<int:analysis_id>/', BacteriaBalanceView.as_view(), name='bacteria-balance-detail'),
    path('health-markers/', HealthMarkersView.as_view(), name='health-markers'),
    path('health-markers/<int:analysis_id>/', HealthMarkersView.as_view(), name='health-markers-detail'),
    path('score-history/', ScoreHistoryView.as_view(), name='score-history'),
    path('request-kit/', RequestNewKitView.as_view(), name='request-kit'),
    path('create-sample/', CreateSampleAnalysisView.as_view(), name='create-sample'),
]
