from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import Dater
from swipe.models import Connection
class Message(models.Model):
    sender = models.ForeignKey(Dater, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(Dater, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not Connection.is__matched(self.sender, self.receiver):
            raise ValidationError("Users are not matched.")