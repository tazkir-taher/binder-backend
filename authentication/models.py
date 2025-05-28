from django.db import models
from django.contrib.auth.models import AbstractUser

class Dater(AbstractUser):
    username = None

    class Gender(models.TextChoices):
        MALE   = 'male',   'Male'
        FEMALE = 'female', 'Female'
        OTHER  = 'other',  'Other'

    email      = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender     = models.CharField(max_length=10, choices=Gender.choices, default=Gender.OTHER)
    
    location  = models.CharField(max_length=100, blank=True, null=True)
    height    = models.PositiveIntegerField(blank=True, null=True)
    bio       = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    hobbies   = models.TextField(blank=True, null=True)
    photo     = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
