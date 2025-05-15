from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions    import IsAuthenticated
from rest_framework.response       import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from authentication.models import Dater
from swipe.models          import Connection
from .models               import Message
from .serializers          import MessageSerializer, ChatPreviewSerializer
from .permissions          import IsMatchedWithRecipient

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsMatchedWithRecipient])
def send_message(request):
   
    sender       = request.user
    recipient_id = request.data['recipient_id']
    content      = request.data['content']

    recipient = Dater.objects.get(id=recipient_id)
    msg = Message.objects.create(sender=sender, recipient=recipient, content=content)
    return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsMatchedWithRecipient])
def get_conversation(request, user_id):
    
    me = request.user
    other = Dater.objects.get(id=user_id)

    msgs = Message.objects.filter(
        Q(sender=me, recipient=other) |
        Q(sender=other, recipient=me)
    ).order_by('timestamp')

    return Response(MessageSerializer(msgs, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recent_chats(request):
    
    me = request.user

    conns = Connection.objects.filter(
        Q(user1=me, user1_liked=True, user2_liked=True) |
        Q(user2=me, user1_liked=True, user2_liked=True)
    ).filter(matched_at__isnull=False)

    matched_ids = [
        conn.user2_id if conn.user1_id == me.id else conn.user1_id
        for conn in conns
    ]

    previews = []
    for uid in matched_ids:
        last = Message.objects.filter(
            Q(sender=me, recipient_id=uid) |
            Q(sender_id=uid, recipient=me)
        ).order_by('-timestamp').first()
        if last:
            previews.append(last)

    return Response(
        ChatPreviewSerializer(previews, many=True, context={'request': request}).data,
        status=status.HTTP_200_OK
    )
