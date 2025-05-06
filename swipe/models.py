from django.db import models
from django.conf import settings

class Swipe(models.Model):
    SWIPE_TYPE = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    
    swiper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='swipes_made'
    )
    swiped = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='swipes_received'
    )
    type = models.CharField(max_length=10, choices=SWIPE_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'swiped')

    def __str__(self):
        return f"{self.swiper} {self.type}d {self.swiped}"