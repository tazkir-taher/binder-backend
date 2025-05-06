# user_profile/views.py

from rest_framework.decorators   import api_view, authentication_classes, permission_classes
from rest_framework.permissions  import IsAuthenticated
from rest_framework.response     import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import ProfileSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = request.user.profile

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        data = {
            k: v for k, v in serializer.data.items()
            if v not in (None, '')
        }
        return Response(data, status=status.HTTP_200_OK)

    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
