from django.contrib.auth.models import User
from rest_framework import serializers
from user.models import Profile
    
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}
    
    class ProfileSerializer(serializers.ModelSerializer):
        user = serializers.PrimaryKeyRelatedField(read_only=True)
    
        class Meta:
            model = Profile
            fields = ('user', 'gender', 'age', 'location')