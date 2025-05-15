from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import Dater
from user_profile.serializers import ProfileSerializer
from .models import Connection
from .serializers import FeedUserSerializer, MatchSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def swipe_feed(request):
    
    me = request.user

    conns = Connection.objects.filter(Q(user1=me) | Q(user2=me))
    seen_ids = set()
    for c in conns:
        seen_ids.add(c.user1.id)
        seen_ids.add(c.user2.id)
    seen_ids.discard(me.id)

    qs = Dater.objects.exclude(id=me.id).exclude(id__in=seen_ids)

    if me.gender == 'male':
        qs = qs.filter(gender='female')
    elif me.gender == 'female':
        qs = qs.filter(gender='male')

    serializer = FeedUserSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def swipe_post(request):
    me = request.user
    swiped_id = request.data.get('swiped_user_id')
    liked     = request.data.get('liked')

    if swiped_id is None or liked is None:
        return Response(
            {"detail": "swiped_user_id and liked are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    u1, u2 = sorted([me.id, swiped_id])
    try:
        other = Dater.objects.get(id=swiped_id)
    except Dater.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    conn, created = Connection.objects.get_or_create(user1_id=u1, user2_id=u2)

    if me.id == conn.user1_id:
        conn.user1_liked = liked
    else:
        conn.user2_liked = liked

    if conn.user1_liked and conn.user2_liked and conn.matched_at is None:
        conn.matched_at = timezone.now()

    conn.save()
    return Response({"message": "Swipe recorded."}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def matches_list(request):
    me = request.user
    qs = Connection.objects.filter(
        Q(user1=me, user2_liked=True, user1_liked=True) |
        Q(user2=me, user1_liked=True, user2_liked=True)
    ).filter(matched_at__isnull=False)
    serializer = MatchSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, user_id):
    me = request.user
    u1, u2 = sorted([me.id, user_id])
    try:
        conn = Connection.objects.get(user1_id=u1, user2_id=u2)
    except Connection.DoesNotExist:
        return Response({"detail": "Not matched with this user."},
                        status=status.HTTP_403_FORBIDDEN)

    if not (conn.user1_liked and conn.user2_liked):
        return Response({"detail": "Not a mutual match."},
                        status=status.HTTP_403_FORBIDDEN)

    other = me if me.id != user_id else None  
    other = Dater.objects.get(id=user_id)
    profile = other.profile
    serializer = ProfileSerializer(profile)
    data = {k: v for k, v in serializer.data.items() if v not in (None, '', [])}
    return Response(data, status=status.HTTP_200_OK)
