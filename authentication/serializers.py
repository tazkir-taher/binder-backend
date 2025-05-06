from rest_framework import serializers
from .models import Dater

class DaterRegistrationSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm password", min_length=8)
    age       = serializers.ReadOnlyField()

    class Meta:
        model = Dater
        fields = (
            'username',
            'first_name', 'last_name',
            'email',
            'birth_date', 'gender',
            'age',
            'password', 'password2',
        )
