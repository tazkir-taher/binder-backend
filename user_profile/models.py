from django.db import models
from django.conf import settings

class DaterProfile(models.Model):
    user      = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    location  = models.CharField(max_length=100, blank=True, null=True)
    height    = models.PositiveIntegerField(blank=True, null=True)
    bio       = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    hobbies   = models.TextField(blank=True, null=True)
    photo     = models.ImageField(
        upload_to='profile_photos/',  # stored in MEDIA_ROOT/profile_photos/
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.email}'s Profile"
