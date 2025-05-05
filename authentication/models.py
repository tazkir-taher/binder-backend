from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

class Dater(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Uses phone_number as the primary identifier instead of username.
    """
    phone_number = models.CharField(max_length=15, unique=True)  # Unique phone number for each user
    is_verified = models.BooleanField(default=False)  # Track if phone number is verified
    profile_completed = models.BooleanField(default=False)  # Track if user has completed their profile
    otp = models.CharField(max_length=6, null=True, blank=True)  # Store OTP code for verification
    otp_expiry = models.DateTimeField(null=True, blank=True)  # Store when the OTP expires
    
    # Use phone_number as the main identifier instead of username
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']  # Required fields during superuser creation

    def generate_otp(self):
        """Generate a 6-digit OTP and set expiry to 5 minutes from now"""
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=5)
        self.save()
        return self.otp

    def verify_otp(self, otp):
        """
        Verify the provided OTP matches and hasn't expired.
        If valid, mark user as verified and clear OTP data.
        """
        if (self.otp == otp and 
            self.otp_expiry and 
            timezone.now() < self.otp_expiry):
            self.is_verified = True
            self.otp = None
            self.otp_expiry = None
            self.save()
            return True
        return False

class OTP(models.Model):
    """
    Separate model to track OTPs for verification and password resets.
    This allows for multiple OTPs per phone number and tracking usage.
    """
    phone_number = models.CharField(max_length=15)  # Phone number the OTP was sent to
    otp = models.CharField(max_length=6)  # The actual OTP code
    created_at = models.DateTimeField(auto_now_add=True)  # When the OTP was created
    is_used = models.BooleanField(default=False)  # Whether the OTP has been used

    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'otp']),  # Index for faster lookups
        ]