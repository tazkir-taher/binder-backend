from rest_framework import serializers
from .models import Dater

class DaterRegistrationSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8, label="Confirm password")

    class Meta:
        model  = Dater
        fields = [
            'first_name', 'last_name',
            'email', 'birth_date', 'gender',
            'password', 'password2',
        ]


class DaterSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model  = Dater
        fields = [
            'id', 'first_name', 'last_name',
            'email', 'birth_date', 'gender', 'age',
            'location', 'height', 'bio',
            'interests', 'hobbies', 'photo',
        ]
        read_only_fields = ['id', 'email', 'age', 'gender', 'birth_date']
        
    def get_age(self, obj):
        return obj.age
    
class ChangePasswordSerializer(serializers.ModelSerializer):
    
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    class Meta:
        model = Dater
        fields = [ 'password', 'new_password1', 'new_password2']


class ForgotPasswordSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    class Meta:
        model = Dater
        fields = ['new_password1', 'new_password2']