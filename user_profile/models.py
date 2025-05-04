from django.db import models
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[ 
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')
    ])
    location = models.CharField(max_length=255, blank=True)
    interests = models.ManyToManyField(
        'Interest',
        through='UserInterest',
        related_name='profiles'
    )

    # Adding related_name to avoid clashes with the default User model fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='profile_groups',  # Specify a related name for the reverse relation
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='profile_permissions',  # Specify a related name for the reverse relation
        blank=True
    )

    def __str__(self):
        return self.username

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'interest')
        ordering = ['-created_at']
