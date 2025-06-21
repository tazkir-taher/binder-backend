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
    candidates = Dater.objects.filter(gender__in=opposite).exclude(id__in=seen_ids).exclude(id=swiper.id).exclude(is_active = False)

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
            return Response({"message": "min_age must be an integer.",
                              "code": 400})
    conn_search.save()

    max_age_value = request.data.get("max_age")
    if max_age_value is not None:
        try:
            conn_search.max_age = int(max_age_value)
        except (ValueError, TypeError):
            return Response({"message": "max_age must be an integer.",
                             "code": 400})
    conn_search.save()

    interest_filter_value = request.data.get("interest_filter")
    if interest_filter_value:
        if isinstance(interest_filter_value, (list, tuple)):
            conn_search.interests = ','.join(map(str, interest_filter_value))
        else:
            conn_search.interests = str(interest_filter_value)
    else:
        conn_search.interests = None
    conn_search.save(update_fields=['interests'])

    candidates = Dater.objects.exclude(id=user.id)
    if user.gender == 'male':
        opposites = ['female']
    else:
        opposites = ['male']
    candidates = candidates.filter(gender__in=opposites)

    seen_ids = Connection.objects.filter(sender=user).values_list('receiver_id', flat=True)
    candidates = candidates.exclude(id__in=seen_ids).exclude(is_active=False)

    today = date.today()
    if conn_search.max_age is not None:
        cutoff_for_max = today - relativedelta(years=conn_search.max_age + 1)
        candidates = candidates.filter(birth_date__gte=cutoff_for_max)
    if conn_search.min_age is not None:
        cutoff_for_min = today - relativedelta(years=conn_search.min_age)
        candidates = candidates.filter(birth_date__lte=cutoff_for_min)
    candidates = candidates.filter(birth_date__isnull=False)

    need = conn_search.interests
    if isinstance(need, list):
        want = need
    elif isinstance(need, str) and need:
        want = [i.strip() for i in need.split(',')]
    else:
        want = []

    similar = []
    for person in candidates:
        been = person.interests
        if isinstance(been, list):
            has = been
        elif isinstance(been, str) and been:
            has = [i.strip() for i in been.split(',')]
        else:
            has = []
        if any(interest in has for interest in want):
            similar.append(person)

    candidates = similar

    lock = request.data.get("lock") is True
    conn_search.lock = lock
    conn_search.save(update_fields=['lock'])

    serializer = DaterSerializer(candidates, many=True)
    return Response({
        "message": "Search results fetched successfully.",
        "code": 200,
        "data": serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search(request):
    user = request.user
    conn_search = ConnectionSearch.objects.filter(owner=user).first()

    if not conn_search:
        return Response({
            "message": "No saved search preferences found.",
            "code": 404
        })

    serializer = ConnectionSearchSerializer(conn_search)
    return Response({
        "message": "Search preferences retrieved successfully.",
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
        Connection.objects.get_or_create(sender=swiper, receiver=receiver)
        matched = False
        return Response({
            "message": "Skipped.",
            "code": status.HTTP_200_OK,
            "data": {"matched": matched,
                     "receiver_name": receiver.first_name,
                     "receiver_id": receiver.id }
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

    matches = [
        conn.receiver if conn.sender == user else conn.sender
        for conn in list(sent) + list(received)
    ]
    serializer = DaterSerializer(matches, many=True, context={'request': request})
    return Response({
        "message": "Matches fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": serializer.data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def match_detail(request, user_id):
    me = request.user

    as_sender = Connection.objects.filter(sender=me, receiver_id=user_id, matched=True).first()
    as_receiver = Connection.objects.filter(sender_id=user_id, receiver=me, matched=True).first()
    if not (as_sender or as_receiver):
        return Response({
            "message": "Not a mutual match.",
            "code": status.HTTP_403_FORBIDDEN
        }, status=status.HTTP_403_FORBIDDEN)

    conn = as_sender if as_sender else as_receiver

    if conn.sender == me:
        other = conn.receiver
    else:
        other = conn.sender

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

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def liked_list(request):
    me = request.user
    conns = Connection.objects.filter(
        receiver=me,
        matched=False
    )

    admirers = [conn.sender for conn in conns]

    serializer = DaterSerializer(admirers, many=True, context={'request': request})
    return Response({
        "message": "People who liked you fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": serializer.data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_detail(request, user_id):
    me = request.user
    conn = Connection.objects.filter(
        sender_id=user_id,
        receiver=me,
        matched=False
    ).first()

    if not conn:
        return Response({
            "message": "Did not like you.",
            "code": status.HTTP_403_FORBIDDEN
        }, status=status.HTTP_403_FORBIDDEN)

    other = conn.sender

    serializer = DaterSerializer(other, context={'request': request})
    cleaned = {k: v for k, v in serializer.data.items() if v not in (None, '', [], {})}

    return Response({
        "message": "Like detail fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": cleaned
    })

#test stuff

@api_view(['DELETE'])
def connection_Delete(request, pk):
    try:
        conn = Connection.objects.get(id= pk)
        conn.delete()
        return Response({
            'code': status.HTTP_200_OK,
            'response': "Data Deleted"
        })
    except Exception as e:
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'response': "Data not Found",
            'error': str(e)
        })

@api_view(['DELETE'])
def connection_Delete_all(request):
    try:
        Connection.objects.all().delete()
        return Response({
            'code': status.HTTP_200_OK,
            'response': "All Data Deleted"
        })
    except Exception as e:
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'response': "Data not Found",
            'error': str(e)
        })