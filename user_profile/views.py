from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ProfileSerializer, ProfileCompletionSerializer
from authentication.models import Dater

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    try:
        user = request.user
        
        if request.method == 'GET':
            serializer = ProfileSerializer(user.profile)
            return Response({
                'profile_data': serializer.data,
                'profile_completed': user.profile_completed
            })
        
        if request.method == 'PUT':
            if not user.profile_completed:
                completion_serializer = ProfileCompletionSerializer(
                    data=request.data,
                    context={'user': user}
                )
                if completion_serializer.is_valid():
                    user = completion_serializer.save()
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'code': status.HTTP_200_OK,
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh),
                        'profile_completed': True
                    })
                return Response(
                    completion_serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Regular profile updates
            profile_serializer = ProfileSerializer(
                user.profile, 
                data=request.data, 
                partial=True
            )
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(profile_serializer.data)
            return Response(
                profile_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)