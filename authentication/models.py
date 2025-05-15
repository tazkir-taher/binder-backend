from datetime import date
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
    gender     = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.OTHER,
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = [] 

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        had_bday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return years if had_bday else years - 1

    @property
    def like_count(self):
        return self.swipes_received.filter(liked=True).count()
