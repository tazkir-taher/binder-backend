import base64
import mimetypes
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import DaterProfile
from .serializers import ProfileSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET:  Return the current user's profile (omitting empty/null fields).
    POST: Update user/profile fields, including base64-encoded 'photo'.
    """
    user = request.user
    profile, _ = DaterProfile.objects.get_or_create(user=user)

    data = request.data.copy()

    # Handle base64 photo if provided
    if 'photo' in data and data['photo']:
        fmt, img_str = data['photo'].split(';base64,')
        ext = fmt.split('/')[-1]  # e.g. 'png' or 'jpeg'
        img_file = ContentFile(base64.b64decode(img_str), name=f"profile.{ext}")
        data['photo'] = img_file
    else:
        data.pop('photo', None)

    if request.method == 'POST':
        # Update core user fields
        user_updated = False
        for field in ['first_name', 'last_name', 'email', 'gender']:
            if field in data:
                setattr(user, field, data[field])
                user_updated = True
        if 'password' in data:
            user.set_password(data['password'])
            user_updated = True
        if user_updated:
            user.save()

        # Update profile-specific fields
        profile_updated = False
        for field in ['location', 'height', 'bio', 'interests', 'hobbies', 'photo']:
            if field in data:
                setattr(profile, field, data[field])
                profile_updated = True
        if profile_updated:
            profile.save()

    # Serialize and return (omitting null/empty)
    serializer = ProfileSerializer(profile, context={'request': request})
    response_data = {
        k: v for k, v in serializer.data.items()
        if v not in (None, '', [], {})
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_media(request, path):
    """
    Stream any file at `path` via whatever storage backend is configured.
    E.g. /media/profile_photos/profile.jpeg → default_storage.open("profile_photos/profile.jpeg")
    """
    if not default_storage.exists(path):
        raise Http404(f"Media '{path}' not found")

    file_handle = default_storage.open(path, mode='rb')
    content_type, _ = mimetypes.guess_type(path)
    return FileResponse(
        file_handle,
        content_type=content_type or 'application/octet-stream',
        status=status.HTTP_200_OK
    )