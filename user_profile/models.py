from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )    
    location = models.CharField(max_length=100, blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"