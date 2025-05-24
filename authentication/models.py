from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class DaterManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

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
    REQUIRED_FIELDS = []  # you can add 'gender' here if you want to prompt for it

    objects = DaterManager()  # 🔥 The Magic Line

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return years if had_birthday else years - 1

    @property
    def like_count(self):
        return self.swipes_received.filter(liked=True).count()
