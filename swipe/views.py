from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from user_profile.models import Profile
from authentication.models import Dater
from user_profile.serializers import ProfileSerializer
from .models import Swipe, Match
from .serializers import UserCardSerializer, SwipeSerializer, MatchSerializer, FeedUserSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def swipe_feed(request):
    me = request.user
    swiped_ids = Swipe.objects.filter(swiper=me).values_list('swiped_id', flat=True)
    qs = Dater.objects.exclude(id=me.id).exclude(id__in=swiped_ids)

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
    swiper = request.user
    swiped_id = request.data.get('swiped_user_id')
    liked = request.data.get('liked')

    if not swiped_id or liked is None:
        return Response({"detail": "swiped_user_id and liked are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        swiped = Dater.objects.get(id=swiped_id)
    except Dater.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if Swipe.objects.filter(swiper=swiper, swiped=swiped).exists():
        return Response({"detail": "You already swiped on this user."}, status=status.HTTP_400_BAD_REQUEST)

    Swipe.objects.create(swiper=swiper, swiped=swiped, liked=liked)

    if liked:
        if Swipe.objects.filter(swiper=swiped, swiped=swiper, liked=True).exists():
            user1, user2 = sorted([swiper, swiped], key=lambda x: x.id)
            Match.objects.get_or_create(user1=user1, user2=user2)

    return Response({"message": "Swipe recorded."}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def matches_list(request):
    user = request.user
    matches = Match.objects.filter(Q(user1=user) | Q(user2=user))
    serializer = MatchSerializer(matches, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, user_id):
    me = request.user

    is_matched = Match.objects.filter(
        Q(user1=me, user2_id=user_id) |
        Q(user2=me, user1_id=user_id)
    ).exists()

    if not is_matched:
        return Response(
            {'detail': "You are not matched with this user."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        other_profile = Dater.objects.get(id=user_id).profile
    except (Dater.DoesNotExist, Profile.DoesNotExist):
        return Response({'detail': "User or Profile not found."},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = ProfileSerializer(other_profile)
    data = { k:v for k,v in serializer.data.items() if v not in (None, '', []) }
    return Response(data, status=status.HTTP_200_OK)
