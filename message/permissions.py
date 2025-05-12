from rest_framework.permissions import BasePermission
from swipe.models import Match
from django.db.models import Q
from authentication.models import Dater

class IsMatchedWithRecipient(BasePermission):
   
    def has_permission(self, request, view):
        recipient_id = request.data.get('recipient_id') or view.kwargs.get('user_id')
        if not recipient_id:
            return False
        try:
            recipient = Dater.objects.get(id=recipient_id)
        except Dater.DoesNotExist:
            return False

        me = request.user
        return Match.objects.filter(
            Q(user1=me, user2=recipient) | Q(user1=recipient, user2=me)
        ).exists()
