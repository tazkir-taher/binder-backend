from rest_framework.permissions import BasePermission
from swipe.models import Connection
from django.contrib.auth import get_user_model

User = get_user_model()

class IsMatchedWithRecipient(BasePermission):

    def has_permission(self, request, view):

        recipient_id = request.data.get('recipient_id') or view.kwargs.get('user_id')
        if not recipient_id:
            return False

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return False

        sender = request.user
        u1, u2 = sorted([sender.id, recipient.id])


        return Connection.objects.filter(
            user1_id=u1,
            user2_id=u2,
            user1_liked=True,
            user2_liked=True,
            matched_at__isnull=False
        ).exists()
