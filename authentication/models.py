from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser

class Dater(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    first_name = models.CharField(max_length=150, unique=True)
    last_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
    max_length=10,
    choices=Gender.choices,
    default=Gender.OTHER,
    )

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return years if had_birthday else years - 1