from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from .models import (
    DailyWellnessCheck,
    HealthMetric,
    SymptomLog,
    WeeklyInsight,
    Routine,
    RoutineLog
)
from .serializers import (
    DailyWellnessCheckSerializer,
    HealthMetricSerializer,
    SymptomLogSerializer,
    WeeklyInsightSerializer,
    RoutineSerializer,
    RoutineLogSerializer,
    WellnessSummarySerializer
)


class TrackingDashboardView(APIView):
    """Get all tracking data for dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get latest microbiome score
        from microbiome.models import MicrobiomeAnalysis
        latest_analysis = MicrobiomeAnalysis.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()
        
        current_score = latest_analysis.overall_score if latest_analysis else 0
        
        # Get previous score for change calculation
        previous_analysis = MicrobiomeAnalysis.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at')[1:2].first()
        
        score_change = 0
        if latest_analysis and previous_analysis:
            score_change = latest_analysis.overall_score - previous_analysis.overall_score
        
        # Get score history (last 6 months)
        from microbiome.models import AnalysisHistory
        score_history = AnalysisHistory.objects.filter(
            user=user
        ).order_by('date')[:12]
        
        history_data = [
            {
                'date': h.date.strftime('%b'),
                'score': h.overall_score,
                'diversity': h.diversity_score,
                'inflammation': h.inflammation_score,
            }
            for h in score_history
        ]
        
        # Get wellness categories summary
        categories = ['digestive', 'energy', 'sleep', 'skin']
        wellness_categories = []
        
        for cat in categories:
            avg = DailyWellnessCheck.objects.filter(
                user=user,
                category=cat
            ).aggregate(Avg('rating'))['rating__avg'] or 0
            
            wellness_categories.append({
                'category': cat,
                'category_display': dict(DailyWellnessCheck.CATEGORY_CHOICES).get(cat, cat),
                'average_rating': round(avg, 1),
                'icon': self._get_category_icon(cat)
            })
        
        # Calculate days until next test
        next_test_days = 45
        if latest_analysis and latest_analysis.next_test_date:
            days_until = (latest_analysis.next_test_date - datetime.now().date()).days
            next_test_days = max(0, days_until)
        
        # Get weekly insights
        insights = WeeklyInsight.objects.filter(
            user=user
        ).order_by('-created_at')[:3]
        
        # Get active routines
        routines = Routine.objects.filter(
            user=user,
            is_active=True
        ).order_by('time_of_day')[:3]
        
        return Response({
            'current_score': current_score,
            'score_change': score_change,
            'score_history': history_data,
            'wellness_categories': wellness_categories,
            'next_test_days': next_test_days,
            'weekly_insights': WeeklyInsightSerializer(insights, many=True).data,
            'routines': RoutineSerializer(routines, many=True).data,
        })
    
    def _get_category_icon(self, category):
        icons = {
            'digestive': 'digestive',
            'energy': 'energy',
            'sleep': 'sleep',
            'skin': 'skin',
        }
        return icons.get(category, 'default')


class WellnessCheckCreateView(APIView):
    """Create a new wellness check"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        
        # Check if check already exists for this date/category
        existing = DailyWellnessCheck.objects.filter(
            user=request.user,
            date=data.get('date'),
            category=data.get('category')
        ).first()
        
        if existing:
            serializer = DailyWellnessCheckSerializer(existing, data=data, partial=True)
        else:
            serializer = DailyWellnessCheckSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WellnessCheckListView(generics.ListAPIView):
    """List wellness checks for user"""
    serializer_class = DailyWellnessCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailyWellnessCheck.objects.filter(
            user=self.request.user
        ).order_by('-date')[:30]


class HealthMetricCreateView(APIView):
    """Create a new health metric entry"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data.copy()
        
        # Auto-set unit based on metric type
        units = {
            'weight': 'kg',
            'bmi': '',
            'waist': 'cm',
            'blood_pressure_systolic': 'mmHg',
            'blood_pressure_diastolic': 'mmHg',
            'blood_glucose': 'mg/dL',
            'heart_rate': 'bpm',
        }
        
        if data.get('metric_type') in units:
            data['unit'] = units[data['metric_type']]
        
        serializer = HealthMetricSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthMetricListView(generics.ListAPIView):
    """List health metrics for user"""
    serializer_class = HealthMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        metric_type = self.request.query_params.get('type')
        queryset = HealthMetric.objects.filter(user=self.request.user)
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        return queryset.order_by('-date')[:50]


class SymptomLogCreateView(APIView):
    """Create a new symptom log"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data.copy()
        
        serializer = SymptomLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SymptomLogListView(generics.ListAPIView):
    """List symptom logs for user"""
    serializer_class = SymptomLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SymptomLog.objects.filter(
            user=self.request.user
        ).order_by('-date')[:30]


class WeeklyInsightsView(generics.ListAPIView):
    """List weekly insights for user"""
    serializer_class = WeeklyInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WeeklyInsight.objects.filter(
            user=self.request.user
        ).order_by('-week_start')[:10]


class MarkInsightReadView(APIView):
    """Mark an insight as read"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            insight = WeeklyInsight.objects.get(pk=pk, user=request.user)
            insight.is_read = True
            insight.save()
            return Response({'message': 'Insight marqué comme lu'})
        except WeeklyInsight.DoesNotExist:
            return Response(
                {'error': 'Insight non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


class RoutineListView(generics.ListAPIView):
    """List user's routines"""
    serializer_class = RoutineSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Routine.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('time_of_day')


class RoutineCreateView(APIView):
    """Create a new routine"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data.copy()
        
        serializer = RoutineSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoutineLogCreateView(APIView):
    """Log routine completion"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data.copy()
        routine_id = data.get('routine')
        
        try:
            routine = Routine.objects.get(pk=routine_id, user=request.user)
        except Routine.DoesNotExist:
            return Response(
                {'error': 'Routine non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        log, created = RoutineLog.objects.get_or_create(
            routine=routine,
            date=data.get('date'),
            defaults={'completed': data.get('completed', True)}
        )
        
        if not created:
            log.completed = data.get('completed', True)
            log.save()
        
        return Response({
            'message': 'Routine enregistrée',
            'completed': log.completed
        })


# Demo data initialization
class InitializeTrackingDataView(APIView):
    """Initialize sample tracking data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Create sample wellness checks
        categories = ['digestive', 'energy', 'sleep', 'skin']
        import random
        
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            for cat in categories:
                DailyWellnessCheck.objects.get_or_create(
                    user=user,
                    date=date,
                    category=cat,
                    defaults={'rating': random.randint(3, 5)}
                )
        
        # Create sample weekly insight
        WeeklyInsight.objects.get_or_create(
            user=user,
            week_start=datetime.now().date() - timedelta(days=7),
            defaults={
                'week_end': datetime.now().date(),
                'title': 'Boost de diversité',
                'description': 'Votre consommation accrue de Fonio a favorisé la croissance de Bifidobacterium, améliorant votre score de 5pts cette semaine.',
                'insight_type': 'positive',
                'related_food': 'Fonio',
                'score_change': 5
            }
        )
        
        # Create sample routines
        routines_data = [
            {
                'name': 'Lait caillé fermenté',
                'routine_type': 'morning',
                'description': 'Naturellement riche en probiotiques',
                'time_of_day': '08:00'
            },
        ]
        
        created_routines = []
        for routine_data in routines_data:
            routine, created = Routine.objects.get_or_create(
                user=user,
                name=routine_data['name'],
                defaults=routine_data
            )
            if created:
                created_routines.append(routine.name)
        
        return Response({
            'message': 'Données de suivi initialisées',
            'wellness_checks_created': 28,
            'routines_created': created_routines
        })
