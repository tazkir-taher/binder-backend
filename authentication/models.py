from datetime import date
from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import AbstractUser

class Dater(AbstractUser):
    username = None

    class Gender(models.TextChoices):
        MALE   = 'male',   'Male'
        FEMALE = 'female', 'Female'

    INTERESTS = (
        ('singing', 'Singing'),
        ('travelling', 'Travelling'),
        ('gaming', 'Gaming'),
        ('photography', 'Photography'),
        ('gardening', 'Gardening'),
    )
    email      = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender     = models.CharField(max_length=10, choices=Gender.choices, default=Gender.FEMALE)
    
    location  = models.CharField(max_length=100, blank=True, null=True)
    height    = models.PositiveIntegerField(blank=True, null=True)
    bio       = models.TextField(blank=True, null=True)
    interests = MultiSelectField(choices=INTERESTS, blank=True, null=True)
    hobbies   = models.TextField(blank=True, null=True)
    mandatory_image    = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    optional_image1    = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    optional_image2    = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    optional_image3    = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)


    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            years = today.year - self.birth_date.year
            had_bday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
            return years if had_bday else years - 1
        return None
    
    @property
    def like_count(self):
        return self.received_connections.filter(matched=False).count()

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
    
class ProfilesHasOTP(models.Model):
    user = models.ForeignKey(Dater, on_delete=models.CASCADE, related_name='profile_otp', null=True)
    otp = models.CharField(max_length=6, null=True, unique=True)
    verified = models.BooleanField(default=False)