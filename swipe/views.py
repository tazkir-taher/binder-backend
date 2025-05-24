from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import Dater
from .models import Connection
from .serializers import ConnectionSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def feed(request):
    swiper = request.user
    opposite = 'female' if swiper.gender == 'male' else 'male'

    sent_ids = Connection.objects.filter(sender=swiper).values_list('receiver_id', flat=True)
    received_ids = Connection.objects.filter(receiver=swiper).values_list('sender_id', flat=True)
    excluded = set(sent_ids) | set(received_ids) | {swiper.id}

    candidates = Dater.objects.filter(gender=opposite).exclude(id__in=excluded)
    data = []
    for user in candidates:
        data.append({
            'id': user.id,
            'username': user.username,
            'gender': user.gender,
            'profile_url': request.build_absolute_uri(user.profile.photo.url) if hasattr(user, 'profile') and user.profile.photo else None,
        })
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def swipe(request):
    swiper = request.user
    receiver_id = request.data.get('receiver_id')
    like = request.data.get('like')

    if receiver_id is None or like is None:
        return Response({'detail': 'receiver_id and like are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        receiver = Dater.objects.get(id=receiver_id)
    except Dater.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if receiver == swiper:
        return Response({'detail': "You can't swipe on yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if not like:
        return Response({'detail': 'Skipped.'}, status=status.HTTP_200_OK)

    try:
        reverse_conn = Connection.objects.get(sender=receiver, receiver=swiper)
        reverse_conn.matched = True
        reverse_conn.save()

        conn = reverse_conn
        matched = True
    except Connection.DoesNotExist:
        conn = Connection.objects.get_or_create(sender=swiper, receiver=receiver)
        matched = False

    serializer = ConnectionSerializer(conn, context={'request': request})
    return Response({'connection': serializer.data, 'matched': matched}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def matches_list(request):
    swiper = request.user
    conns = Connection.objects.filter(
        Q(sender=swiper) | Q(receiver=swiper),
        matched=True
    )
    results = []
    for conn in conns:
        other = conn.receiver if conn.sender == swiper else conn.sender
        user_data = {
            'id': other.id,
            'username': other.username,
        }
        results.append({
            'user': user_data,
            'matched_at': conn.matched_at,
        })
    return Response(results, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, user_id):
    swiper = request.user
    conn = Connection.objects.filter(
        Q(sender=swiper, receiver_id=user_id) | Q(sender_id=user_id, receiver=swiper),
        matched=True
    ).first()

    if not conn:
        return Response({'detail': 'Not a mutual match.'}, status=status.HTTP_403_FORBIDDEN)

    other = Dater.objects.get(id=user_id)
    profile = getattr(other, 'profile', None)
    if not profile:
        return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    from user_profile.serializers import ProfileSerializer
    serializer = ProfileSerializer(profile, context={'request': request})
    data = {k: v for k, v in serializer.data.items() if v not in (None, '', [])}
    return Response(data, status=status.HTTP_200_OK)
