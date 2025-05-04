from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import ProfileSerializer

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_detail(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = ProfileSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            user = serializer.save()
 
            if 'password' in request.data:
                user.set_password(request.data['password'])
                user.save()
            
            return Response(ProfileSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)