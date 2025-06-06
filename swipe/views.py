from datetime import date
from dateutil.relativedelta import relativedelta

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import *
from authentication.serializers import *

from .models import *
from .serializers import *

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def feed(request):
    swiper = request.user

    if swiper.gender == 'male':
        opposite = ['female']
    else:
        opposite = ['male']

    seen_ids = Connection.objects.filter(sender=swiper).values_list('receiver_id', flat=True)
    candidates = Dater.objects.filter(gender__in=opposite).exclude(id__in=seen_ids).exclude(id=swiper.id)

    serializer = DaterSerializer(candidates, many=True, context={'request': request})
    return Response({
        "message": "Feed fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search(request):
    user = request.user

    conn_search = ConnectionSearch.objects.filter(owner=user).first()
    if not conn_search:
        conn_search = ConnectionSearch.objects.create(owner=user)

    min_age_value = request.data.get("min_age")
    if min_age_value is not None:
        try:
            conn_search.min_age = int(min_age_value)
        except (ValueError, TypeError):
            return Response({
                "message": "min_age must be an integer.",
                "code": 400
            })
        
    max_age_value = request.data.get("max_age")
    if max_age_value is not None:
        try:
            conn_search.max_age = int(max_age_value)
        except (ValueError, TypeError):
            return Response({
                "message": "max_age must be an integer.",
                "code": 400
            })

    interest_filter_value = request.data.get("interest_filter")
    if interest_filter_value:
        conn_search.interests = interest_filter_value

    conn_search.save()

    candidates = Dater.objects.exclude(id=user.id)

    if user.gender == 'male':
        opposites = ['female']
    else:
        opposites = ['male']
    candidates = candidates.filter(gender__in=opposites)

    seen_ids = Connection.objects.filter(sender=user).values_list('receiver_id', flat=True)
    candidates = candidates.exclude(id__in=seen_ids)

    today = date.today()
    if conn_search.max_age is not None:
        cutoff_for_max = today - relativedelta(years=conn_search.max_age)
        candidates = candidates.filter(birth_date__gte=cutoff_for_max)

    if conn_search.min_age is not None:
        cutoff_for_min = today - relativedelta(years=conn_search.min_age)
        candidates = candidates.filter(birth_date__lte=cutoff_for_min)

    if conn_search.interests:
        candidates = candidates.filter(interests=conn_search.interests)

    candidates = candidates.filter(birth_date__isnull=False)

    serializer = DaterSerializer(candidates, many=True)
    return Response({
        "message": "Search results fetched successfully.",
        "code": 200,
        "data": serializer.data
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def swipe(request):
    swiper = request.user
    receiver_id = request.data.get('receiver_id')
    like = request.data.get('like')

    if receiver_id is None or like is None:
        return Response({
            "message": "receiver_id and like are required.",
            "code": status.HTTP_400_BAD_REQUEST
        })

    try:
        receiver = Dater.objects.get(id=receiver_id)
    except Dater.DoesNotExist:
        return Response({
            "message": "User not found.",
            "code": status.HTTP_400_BAD_REQUEST
        })

    if receiver == swiper:
        return Response({
            "message": "You can't swipe on yourself.",
            "code": status.HTTP_400_BAD_REQUEST
        })

    if not like:
        matched = False
        return Response({
            "message": "Skipped.",
            "code": status.HTTP_200_OK,
            "data": {"matched": matched, "receiver_name": receiver.first_name}
        })

    mutual = Connection.objects.filter(sender=receiver, receiver=swiper, matched=False).exists()

    if mutual:
        Connection.objects.filter(sender=receiver, receiver=swiper).update(matched=True)
        matched = True
    else:
        Connection.objects.get_or_create(sender=swiper, receiver=receiver)
        matched = False

    return Response({
        "message": "Swipe recorded.",
        "code": status.HTTP_200_OK,
        "data": {"matched": matched, "receiver_name": receiver.first_name}
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def likes_received(request):
    user = request.user

    liker_ids = Connection.objects.filter(receiver=user, matched=False).values_list('sender_id', flat=True)

    likers = Dater.objects.filter(id__in=liker_ids)
    serializer = DaterSerializer(likers, many=True, context={'request': request})

    return Response({
        "message": "Likes received fetched successfully.",
        "code": 200,
        "data": serializer.data
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def matches_list(request):
    user = request.user
    sent = Connection.objects.filter(sender=user, matched=True)
    received = Connection.objects.filter(receiver=user, matched=True)
    matches = list(sent) + list(received)
    serializer = ConnectionSerializer(matches, many=True, context={'request': request})
    return Response({
        "message": "Matches fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": serializer.data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, user_id):
    user = request.user
    as_sender = Connection.objects.filter(sender=user, receiver_id=user_id, matched=True).first()
    as_receiver = Connection.objects.filter(sender_id=user_id, receiver=user, matched=True).first()
    if not (as_sender or as_receiver):
        return Response({
            "message": "Not a mutual match.",
            "code": status.HTTP_403_FORBIDDEN
        })

    try:
        other = Dater.objects.get(id=user_id)
    except Dater.DoesNotExist:
        return Response({
            "message": "User not found.",
            "code": status.HTTP_404_NOT_FOUND
        })

    serializer = DaterSerializer(other, context={'request': request})
    data = {
        k: v for k, v in serializer.data.items()
        if v not in (None, '', [], {})
    }
    return Response({
        "message": "Match detail fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": data
    })