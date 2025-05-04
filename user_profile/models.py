from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class Profile(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'
    
    class MBTI(models.TextChoices):
        INTJ = 'INTJ', 'INTJ - Architect'
        INTP = 'INTP', 'INTP - Logician'
        ENTJ = 'ENTJ', 'ENTJ - Commander'
        ENTP = 'ENTP', 'ENTP - Debater'
        INFJ = 'INFJ', 'INFJ - Advocate'
        INFP = 'INFP', 'INFP - Mediator'
        ENFJ = 'ENFJ', 'ENFJ - Protagonist'
        ENFP = 'ENFP', 'ENFP - Campaigner'
        ISTJ = 'ISTJ', 'ISTJ - Logistician'
        ISFJ = 'ISFJ', 'ISFJ - Defender'
        ESTJ = 'ESTJ', 'ESTJ - Executive'
        ESFJ = 'ESFJ', 'ESFJ - Consul'
        ISTP = 'ISTP', 'ISTP - Virtuoso'
        ISFP = 'ISFP', 'ISFP - Adventurer'
        ESTP = 'ESTP', 'ESTP - Entrepreneur'
        ESFP = 'ESFP', 'ESFP - Entertainer'

    class Zodiac(models.TextChoices):
        ARIES = 'aries', '♈ Aries'
        TAURUS = 'taurus', '♉ Taurus'
        GEMINI = 'gemini', '♊ Gemini'
        CANCER = 'cancer', '♋ Cancer'
        LEO = 'leo', '♌ Leo'
        VIRGO = 'virgo', '♍ Virgo'
        LIBRA = 'libra', '♎ Libra'
        SCORPIO = 'scorpio', '♏ Scorpio'
        SAGITTARIUS = 'sagittarius', '♐ Sagittarius'
        CAPRICORN = 'capricorn', '♑ Capricorn'
        AQUARIUS = 'aquarius', '♒ Aquarius'
        PISCES = 'pisces', '♓ Pisces'

    class Diet(models.TextChoices):
        VEGETARIAN = 'vegetarian', 'Vegetarian'
        VEGAN = 'vegan', 'Vegan'
        OMNIVORE = 'omnivore', 'Omnivore'
        PESCATARIAN = 'pescatarian', 'Pescatarian'
        KETO = 'keto', 'Keto'

    # Core Fields
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=255, blank=True)
    
    # Choice-based Fields
    mbti = models.CharField(max_length=4, choices=MBTI.choices, blank=True, null=True)
    zodiac_sign = models.CharField(max_length=12, choices=Zodiac.choices, blank=True, null=True)
    dietary_preference = models.CharField(max_length=12, choices=Diet.choices, blank=True, null=True)

    # Corrected Relationship Field — note the model name!
    interests = models.ManyToManyField(
        'InterestCategory',  # ✅ FIXED this from 'Interest'
        through='UserInterest',
        related_name='profiles'
    )

# The actual interest categories
class InterestCategory(models.Model):
    class Category(models.TextChoices):
        HOBBY = 'hobby', 'Hobby'
        MUSIC = 'music', 'Music Genre'
        SPORT = 'sport', 'Sport'
        LANGUAGE = 'language', 'Language'
        PET = 'pet', 'Pet Preference'

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        unique_together = ('name', 'category')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.get_category_display()}: {self.name}"

# Junction table linking users and interests
class UserInterest(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)               # ✅ Correct FK
    interest = models.ForeignKey(InterestCategory, on_delete=models.CASCADE)  # ✅ Correct FK
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'interest')
        ordering = ['-created_at']
