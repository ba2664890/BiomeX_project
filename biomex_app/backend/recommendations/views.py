from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Recommendation, DailyRecommendation
from .serializers import (
    RecommendationSerializer,
    RecommendationListSerializer,
    DailyRecommendationSerializer
)


class UserRecommendationsView(generics.ListAPIView):
    """Get all recommendations for the current user"""
    serializer_class = RecommendationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            is_completed=False
        ).order_by('-created_at')


class RecommendationDetailView(APIView):
    """Get detailed recommendation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        recommendation = get_object_or_404(
            Recommendation,
            pk=pk,
            user=request.user
        )
        
        # Mark as read
        if not recommendation.is_read:
            recommendation.is_read = True
            recommendation.save()
        
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data)


class MarkRecommendationReadView(APIView):
    """Mark a recommendation as read"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            recommendation = Recommendation.objects.get(pk=pk, user=request.user)
            recommendation.is_read = True
            recommendation.save()
            return Response({'message': 'Recommandation marquée comme lue'})
        except Recommendation.DoesNotExist:
            return Response(
                {'error': 'Recommandation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkRecommendationCompletedView(APIView):
    """Mark a recommendation as completed"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            recommendation = Recommendation.objects.get(pk=pk, user=request.user)
            recommendation.is_completed = True
            recommendation.completed_at = timezone.now()
            recommendation.save()
            
            # Create notification
            from users.models import UserActivity
            UserActivity.objects.create(
                user=request.user,
                title='Recommandation complétée',
                message=f'Vous avez complété: {recommendation.title}',
                activity_type='recommendation_completed'
            )
            
            return Response({
                'message': 'Recommandation marquée comme complétée',
                'completed_at': recommendation.completed_at
            })
        except Recommendation.DoesNotExist:
            return Response(
                {'error': 'Recommandation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )


class DailyRecommendationsView(APIView):
    """Get today's recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = datetime.now().date()
        
        daily_recs = DailyRecommendation.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )[:5]
        
        if not daily_recs.exists():
            # Return default recommendations if none active
            daily_recs = DailyRecommendation.objects.filter(
                is_active=True
            )[:5]
        
        serializer = DailyRecommendationSerializer(daily_recs, many=True)
        return Response(serializer.data)


class TodaysRecommendationsView(APIView):
    """Get all recommendations for today (personalized + daily)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get personalized recommendations
        personalized = Recommendation.objects.filter(
            user=user,
            is_completed=False
        ).order_by('-priority', '-created_at')[:5]
        
        # Get daily recommendations
        today = datetime.now().date()
        daily = DailyRecommendation.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )[:3]
        
        if not daily.exists():
            daily = DailyRecommendation.objects.filter(is_active=True)[:3]
        
        return Response({
            'personalized': RecommendationSerializer(personalized, many=True).data,
            'daily': DailyRecommendationSerializer(daily, many=True).data,
            'total_count': personalized.count() + daily.count()
        })


# Admin/Demo views
class CreateSampleRecommendationsView(APIView):
    """Create sample recommendations for demo"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Get some foods for recommendations
        from nutrition.models import FoodItem
        
        recommendations_data = [
            {
                'title': 'Arachides locales',
                'description': 'Riche en fibres, favorise la croissance des bactéries bénéfiques.',
                'category': 'food',
                'priority': 'high',
            },
            {
                'title': 'Feuilles de baobab',
                'description': 'Prébiotique naturel, excellent pour la diversité microbienne.',
                'category': 'food',
                'priority': 'medium',
            },
            {
                'title': 'Fonio',
                'description': 'Céréale ancienne riche en méthionine, facilite la digestion.',
                'category': 'food',
                'priority': 'high',
            },
        ]
        
        created_recs = []
        for rec_data in recommendations_data:
            rec, created = Recommendation.objects.get_or_create(
                user=user,
                title=rec_data['title'],
                defaults={
                    'description': rec_data['description'],
                    'category': rec_data['category'],
                    'priority': rec_data['priority'],
                    'expected_score_improvement': 5,
                    'expires_at': timezone.now() + timedelta(days=7)
                }
            )
            if created:
                created_recs.append(rec.title)
        
        # Create daily recommendations
        daily_recs_data = [
            {
                'title': 'Hydratation',
                'description': 'Buvez au moins 2L d\'eau aujourd\'hui pour soutenir votre microbiote.',
                'category': 'hydration',
                'icon': '💧'
            },
            {
                'title': 'Marche quotidienne',
                'description': '30 minutes de marche améliorent la motilité intestinale.',
                'category': 'exercise',
                'icon': '🚶'
            },
        ]
        
        created_daily = []
        for rec_data in daily_recs_data:
            rec, created = DailyRecommendation.objects.get_or_create(
                title=rec_data['title'],
                defaults={
                    'description': rec_data['description'],
                    'category': rec_data['category'],
                    'icon': rec_data['icon'],
                    'is_active': True,
                    'start_date': datetime.now().date(),
                    'end_date': datetime.now().date() + timedelta(days=30)
                }
            )
            if created:
                created_daily.append(rec.title)
        
        return Response({
            'message': 'Recommandations de démonstration créées',
            'personalized_created': created_recs,
            'daily_created': created_daily
        })
