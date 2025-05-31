from django.db import models
from authentication.models import Dater

class Connection(models.Model):
    sender = models.ForeignKey(Dater, related_name='sent_connections', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Dater,related_name='received_connections',on_delete=models.CASCADE)
    matched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} → {self.receiver} | matched={self.matched}"
    
class ConnectionSearch(models.Model):
    interest_filter = models.OneToOneField(Dater, related_name='connection_search', on_delete=models.CASCADE)
    max_age = models.IntegerField(null=True, blank=True)
    min_age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Search by {self.interest_filter.email}: ages {self.min_age}–{self.max_age}"