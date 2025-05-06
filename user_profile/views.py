from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Profile
from .serializers import ProfileSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        data = {
            k: v for k, v in serializer.data.items()
            if v not in (None, '', [])
        }
        return Response(data, status=status.HTTP_200_OK)

    # Handle POST for updates
    profile_fields = ['location', 'height', 'bio', 'interests', 'hobbies']
    user_fields = ['first_name', 'last_name', 'email', 'gender']
    updated = False

    # Update user fields
    for field in user_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
            updated = True

    # Handle password separately
    if 'password' in request.data:
        user.set_password(request.data['password'])
        updated = True

    if updated:
        user.save()

    # Update profile fields
    for field in profile_fields:
        if field in request.data:
            setattr(profile, field, request.data[field])
            updated = True

    if updated:
        profile.save()

    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)
