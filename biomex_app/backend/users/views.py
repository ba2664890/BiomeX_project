from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    UserRegisterSerializer,
    ChangePasswordSerializer,
    UserActivitySerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Utilisateur créé avec succès. Veuillez vous connecter.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': ['Mot de passe actuel incorrect.']}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Mot de passe modifié avec succès.'}, 
            status=status.HTTP_200_OK
        )


class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get latest microbiome score
        from microbiome.models import MicrobiomeAnalysis
        latest_analysis = MicrobiomeAnalysis.objects.filter(
            user=user
        ).order_by('-created_at').first()
        
        # Get unread notifications count
        unread_count = user.activities.filter(is_read=False).count()
        
        # Get recommendations count
        from recommendations.models import Recommendation
        recommendations_count = Recommendation.objects.filter(
            user=user, 
            is_read=False
        ).count()
        
        dashboard_data = {
            'user': UserProfileSerializer(user).data,
            'microbiome_score': latest_analysis.overall_score if latest_analysis else None,
            'species_count': latest_analysis.species_count if latest_analysis else 0,
            'probiotic_count': latest_analysis.probiotic_count if latest_analysis else 0,
            'pathogen_percentage': latest_analysis.pathogen_percentage if latest_analysis else 0,
            'unread_notifications': unread_count,
            'new_recommendations': recommendations_count,
            'has_active_analysis': latest_analysis is not None,
            'next_test_due': latest_analysis.next_test_date if latest_analysis else None,
        }
        
        return Response(dashboard_data)


class UserNotificationsView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.activities.all()


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = request.user.activities.get(pk=pk)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marquée comme lue.'})
        except:
            return Response(
                {'error': 'Notification non trouvée.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
