from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import MicrobiomeAnalysis, BacteriaBalance, HealthMarker, AnalysisHistory
from .serializers import (
    MicrobiomeAnalysisSerializer,
    MicrobiomeAnalysisListSerializer,
    DetailedAnalysisSerializer,
    AnalysisHistorySerializer,
    BacteriaBalanceSerializer,
    HealthMarkerSerializer,
    DashboardScoreSerializer
)


class LatestAnalysisView(APIView):
    """Get the latest analysis for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        analysis = MicrobiomeAnalysis.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-created_at').first()
        
        if not analysis:
            return Response(
                {'message': 'Aucune analyse trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MicrobiomeAnalysisSerializer(analysis)
        return Response(serializer.data)


class AnalysisDetailView(APIView):
    """Get detailed analysis by ID"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        analysis = get_object_or_404(
            MicrobiomeAnalysis, 
            pk=pk, 
            user=request.user
        )
        serializer = DetailedAnalysisSerializer(analysis)
        return Response(serializer.data)


class AnalysisListView(generics.ListAPIView):
    """List all analyses for the current user"""
    serializer_class = MicrobiomeAnalysisListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MicrobiomeAnalysis.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class DashboardScoresView(APIView):
    """Get current scores for dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        analysis = MicrobiomeAnalysis.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-created_at').first()
        
        if not analysis:
            # Return default values if no analysis exists
            return Response({
                'overall_score': 0,
                'diversity_score': 0,
                'inflammation_score': 0,
                'gut_brain_score': 0,
                'status': 'no_data',
                'species_count': 0,
                'probiotic_count': 0,
                'pathogen_percentage': 0,
                'last_updated': None,
                'message': 'Aucune analyse disponible. Commandez votre kit BiomeX pour commencer.'
            })
        
        # Determine status based on score
        if analysis.overall_score >= 80:
            status_text = 'excellent'
        elif analysis.overall_score >= 60:
            status_text = 'tres_bon'
        elif analysis.overall_score >= 40:
            status_text = 'bon'
        else:
            status_text = 'a_ameliorer'
        
        data = {
            'overall_score': analysis.overall_score,
            'diversity_score': analysis.diversity_score,
            'inflammation_score': analysis.inflammation_score,
            'gut_brain_score': analysis.gut_brain_score,
            'status': status_text,
            'species_count': analysis.species_count,
            'probiotic_count': analysis.probiotic_count,
            'pathogen_percentage': analysis.pathogen_percentage,
            'last_updated': analysis.completed_at,
            'next_test_date': analysis.next_test_date,
        }
        
        return Response(data)


class BacteriaBalanceView(APIView):
    """Get bacteria balance for latest or specific analysis"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, analysis_id=None):
        if analysis_id:
            analysis = get_object_or_404(
                MicrobiomeAnalysis,
                pk=analysis_id,
                user=request.user
            )
        else:
            analysis = MicrobiomeAnalysis.objects.filter(
                user=request.user,
                status='completed'
            ).order_by('-created_at').first()
        
        if not analysis:
            return Response(
                {'message': 'Aucune analyse trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        balances = analysis.bacteria_balances.all()
        serializer = BacteriaBalanceSerializer(balances, many=True)
        return Response(serializer.data)


class HealthMarkersView(APIView):
    """Get health markers for latest or specific analysis"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, analysis_id=None):
        if analysis_id:
            analysis = get_object_or_404(
                MicrobiomeAnalysis,
                pk=analysis_id,
                user=request.user
            )
        else:
            analysis = MicrobiomeAnalysis.objects.filter(
                user=request.user,
                status='completed'
            ).order_by('-created_at').first()
        
        if not analysis:
            return Response(
                {'message': 'Aucune analyse trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        markers = analysis.health_markers.all()
        serializer = HealthMarkerSerializer(markers, many=True)
        return Response(serializer.data)


class ScoreHistoryView(APIView):
    """Get score history over time"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        history = AnalysisHistory.objects.filter(
            user=request.user
        ).order_by('date')
        
        serializer = AnalysisHistorySerializer(history, many=True)
        return Response(serializer.data)


class RequestNewKitView(APIView):
    """Request a new test kit"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # In a real implementation, this would create an order
        # and trigger notifications
        
        # Create a pending analysis
        sample_id = f"BMX-{timezone.now().strftime('%Y%m%d')}-{request.user.id:04d}"
        
        analysis = MicrobiomeAnalysis.objects.create(
            user=request.user,
            sample_id=sample_id,
            sample_date=timezone.now().date(),
            status='pending',
            next_test_date=timezone.now().date() + timedelta(days=45)
        )
        
        # Create notification
        from users.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            title='Kit de suivi commandé',
            message='Votre kit de suivi a été commandé avec succès. Vous recevrez une notification dès qu\'il sera expédié.',
            activity_type='kit_ordered'
        )
        
        return Response({
            'message': 'Kit commandé avec succès',
            'sample_id': sample_id,
            'estimated_delivery': '3-5 jours ouvrables'
        })


# Admin/Staff views for creating sample data
class CreateSampleAnalysisView(APIView):
    """Create sample analysis data (for demo purposes)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Create a sample analysis with realistic data
        import random
        
        sample_id = f"BMX-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        analysis = MicrobiomeAnalysis.objects.create(
            user=request.user,
            sample_id=sample_id,
            sample_date=timezone.now().date(),
            status='completed',
            overall_score=random.randint(65, 95),
            diversity_score=random.randint(60, 90),
            inflammation_score=random.randint(70, 95),
            gut_brain_score=random.randint(65, 90),
            species_count=random.randint(700, 1000),
            probiotic_count=random.randint(100, 150),
            pathogen_percentage=round(random.uniform(8, 15), 1),
            shannon_index=round(random.uniform(3.5, 5.0), 2),
            simpson_index=round(random.uniform(0.85, 0.95), 3),
            chao1_index=round(random.uniform(800, 1200), 0),
            percentile_africa=random.randint(60, 90),
            percentile_local=random.randint(55, 85),
            next_test_date=timezone.now().date() + timedelta(days=45),
            summary='Votre microbiote montre une richesse exceptionnelle, typique des régimes riches en fibres de la région.',
            recommendations='Continuez à consommer des aliments fermentés et riches en fibres pour maintenir cette diversité.',
            completed_at=timezone.now()
        )
        
        # Create bacteria balances
        bacteria_data = [
            {'name': 'Bifidobacteria', 'type': 'probiotic', 'pct': random.uniform(15, 25), 'status': 'optimal'},
            {'name': 'Lactobacillus', 'type': 'probiotic', 'pct': random.uniform(8, 15), 'status': 'optimal'},
            {'name': 'Firmicutes', 'type': 'phylum', 'pct': random.uniform(50, 65), 'status': 'elevated'},
            {'name': 'Bacteroidetes', 'type': 'phylum', 'pct': random.uniform(20, 35), 'status': 'low'},
            {'name': 'Akkermansia', 'type': 'beneficial', 'pct': random.uniform(2, 5), 'status': 'optimal'},
            {'name': 'Prevotella', 'type': 'common', 'pct': random.uniform(10, 20), 'status': 'optimal'},
        ]
        
        for bact in bacteria_data:
            BacteriaBalance.objects.create(
                analysis=analysis,
                bacteria_name=bact['name'],
                bacteria_type=bact['type'],
                percentage=round(bact['pct'], 1),
                status=bact['status'],
                reference_min=5 if bact['status'] == 'optimal' else 20,
                reference_max=30 if bact['status'] == 'optimal' else 60,
                description=f'Niveau {bact["status"]} de {bact["name"]} dans votre microbiote.'
            )
        
        # Create health markers
        markers_data = [
            {'name': 'Digestion', 'cat': 'digestive', 'score': random.randint(70, 95)},
            {'name': 'Énergie', 'cat': 'metabolic', 'score': random.randint(65, 90)},
            {'name': 'Sommeil', 'cat': 'mental', 'score': random.randint(60, 85)},
            {'name': 'Peau', 'cat': 'immune', 'score': random.randint(70, 90)},
        ]
        
        for marker in markers_data:
            HealthMarker.objects.create(
                analysis=analysis,
                name=marker['name'],
                category=marker['cat'],
                score=marker['score'],
                status='bon' if marker['score'] >= 70 else 'moyen',
                description=f'Votre score {marker["name"].lower()} est dans la fourchette {"optimale" if marker["score"] >= 80 else "normale"}.'
            )
        
        # Create history entry
        AnalysisHistory.objects.create(
            user=request.user,
            date=timezone.now().date(),
            overall_score=analysis.overall_score,
            diversity_score=analysis.diversity_score,
            inflammation_score=analysis.inflammation_score,
            gut_brain_score=analysis.gut_brain_score,
            notes='Analyse initiale'
        )
        
        return Response({
            'message': 'Analyse de démonstration créée avec succès',
            'analysis_id': analysis.id,
            'sample_id': sample_id
        })
