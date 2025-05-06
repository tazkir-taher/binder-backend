from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username   = serializers.CharField(source='user.username',   read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name  = serializers.CharField(source='user.last_name',  read_only=True)
    email      = serializers.EmailField  (source='user.email',      read_only=True)
    age        = serializers.IntegerField(source='user.age',        read_only=True)
    gender     = serializers.CharField(source='user.gender',     read_only=True)

    class Meta:
        model  = Profile
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'age', 'gender',
            'location', 'height', 'bio',
            'interests', 'hobbies',
        ]
