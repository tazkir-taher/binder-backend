from django.db import models

class Profile(models.Model):
    user = models.OneToOneField('authentication.Dater', on_delete=models.CASCADE, related_name='profile', null=True, blank=True)

    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    class Height(models.TextChoices):
        _4_0 = '4_0', "4'0"
        _4_1 = '4_1', "4'1"
        _7_0 = '7_0', "7'0"

    class Lifestyle(models.TextChoices):
        DRINKING = 'drinking', 'Drinking'
        SMOKING = 'smoking', 'Smoking'
        HAVE_KIDS = 'have_kids', 'Have Kids'
        WANT_KIDS = 'want_kids', 'Want Kids'
        RELIGION = 'religion', 'Religion'
        POLITICAL_VIEWS = 'political_views', 'Political Views'
        CAUSES = 'causes', 'Causes & Communities'

    class Quality(models.TextChoices):
        KINDNESS = 'kindness', 'Kindness'
        HUMOR = 'humor', 'Humor'
        HONESTY = 'honesty', 'Honesty'

    class RelationshipGoal(models.TextChoices):
        DATING = 'dating', 'Dating'
        BFF = 'bff', 'BFF'

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=255, blank=True)

    lifestyle = models.CharField(
        max_length=20,
        choices=Lifestyle.choices,
        blank=True,
        null=True
    )
    height = models.CharField(
        max_length=4,
        choices=Height.choices,
        blank=True,
        null=True
    )
    qualities = models.ManyToManyField(
        'ProfileQuality',
        through='UserQuality',
        related_name='profiles'
    )
    interests = models.ManyToManyField(
        'InterestCategory',
        through='UserInterest',
        related_name='profiles'
    )
    relationship_goal = models.CharField(
        max_length=10,
        choices=RelationshipGoal.choices,
        blank=True,
        null=True
    )
    hoping_for = models.ManyToManyField(
        'ProfileQuality',
        through='HopingFor',
        related_name='hoping_profiles'
    )


class ProfileQuality(models.Model):
    class Meta:
        verbose_name = 'Quality'
        verbose_name_plural = 'Qualities'

    name = models.CharField(max_length=100)
    choice = models.CharField(max_length=20, choices=Profile.Quality.choices)

class UserQuality(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    quality = models.ForeignKey(ProfileQuality, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'quality')

class HopingFor(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    quality = models.ForeignKey(ProfileQuality, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'quality')

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

class UserInterest(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    interest = models.ForeignKey(InterestCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'interest')
        ordering = ['-created_at']