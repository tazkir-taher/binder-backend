from django.db import models
from django.conf import settings

class Message(models.Model):
    sender    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_sent'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_received'
    )
    content   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read      = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"
