from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions    import IsAuthenticated
from rest_framework.response       import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from authentication.models import Dater
from swipe.models         import Match
from .models              import Message
from .serializers         import MessageSerializer, ChatPreviewSerializer
from .permissions         import IsMatchedWithRecipient

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsMatchedWithRecipient])
def send_message(request):
    sender       = request.user
    recipient_id = request.data.get('recipient_id')
    content      = request.data.get('content')

    recipient = Dater.objects.get(id=recipient_id)
    message = Message.objects.create(
        sender=sender,
        recipient=recipient,
        content=content
    )
    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsMatchedWithRecipient])
def get_conversation(request, user_id):
    me = request.user
    other = Dater.objects.get(id=user_id)

    messages = Message.objects.filter(
        Q(sender=me, recipient=other) | Q(sender=other, recipient=me)
    ).order_by('timestamp')

    return Response(
        MessageSerializer(messages, many=True).data,
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recent_chats(request):
    me = request.user

    matches = Match.objects.filter(Q(user1=me) | Q(user2=me))
    matched_ids = [
        m.user2.id if m.user1 == me else m.user1.id
        for m in matches
    ]

    previews = []
    for uid in matched_ids:
        other = Dater.objects.get(id=uid)
        last_msg = Message.objects.filter(
            Q(sender=me, recipient=other) | Q(sender=other, recipient=me)
        ).order_by('-timestamp').first()
        if last_msg:
            previews.append(last_msg)

    serializer = ChatPreviewSerializer(previews, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)