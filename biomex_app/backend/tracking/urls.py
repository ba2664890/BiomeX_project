from django.urls import path
from .views import (
    TrackingDashboardView,
    WellnessCheckCreateView,
    WellnessCheckListView,
    HealthMetricCreateView,
    HealthMetricListView,
    SymptomLogCreateView,
    SymptomLogListView,
    WeeklyInsightsView,
    MarkInsightReadView,
    RoutineListView,
    RoutineCreateView,
    RoutineLogCreateView,
    InitializeTrackingDataView,
)

urlpatterns = [
    path('dashboard/', TrackingDashboardView.as_view(), name='tracking-dashboard'),
    path('wellness/', WellnessCheckListView.as_view(), name='wellness-list'),
    path('wellness/create/', WellnessCheckCreateView.as_view(), name='wellness-create'),
    path('health-metrics/', HealthMetricListView.as_view(), name='health-metrics-list'),
    path('health-metrics/create/', HealthMetricCreateView.as_view(), name='health-metrics-create'),
    path('symptoms/', SymptomLogListView.as_view(), name='symptom-list'),
    path('symptoms/create/', SymptomLogCreateView.as_view(), name='symptom-create'),
    path('insights/', WeeklyInsightsView.as_view(), name='weekly-insights'),
    path('insights/<int:pk>/read/', MarkInsightReadView.as_view(), name='mark-insight-read'),
    path('routines/', RoutineListView.as_view(), name='routine-list'),
    path('routines/create/', RoutineCreateView.as_view(), name='routine-create'),
    path('routines/log/', RoutineLogCreateView.as_view(), name='routine-log'),
    path('initialize-data/', InitializeTrackingDataView.as_view(), name='initialize-tracking-data'),
]
