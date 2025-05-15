from django.db import models
from django.conf import settings

class Connection(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections_as_user2'
    )
    user1_liked = models.BooleanField(default=False)
    user2_liked = models.BooleanField(default=False)
    matched_at  = models.DateTimeField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.id}<–>{self.user2.id}  matched_at={self.matched_at}"
