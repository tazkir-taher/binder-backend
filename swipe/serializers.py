from rest_framework import serializers
from authentication.models import Dater
from .models import Connection

class FeedUserSerializer(serializers.ModelSerializer):
    age       = serializers.IntegerField()
    photo_url = serializers.CharField(read_only=True)
    location  = serializers.CharField(source='profile.location', read_only=True)
    height    = serializers.IntegerField(source='profile.height',    read_only=True)
    bio       = serializers.CharField(source='profile.bio',         read_only=True)
    interests = serializers.CharField(source='profile.interests',   read_only=True)
    hobbies   = serializers.CharField(source='profile.hobbies',     read_only=True)

    class Meta:
        model  = Dater
        fields = [
            'id', 'first_name','last_name','email',
            'age','gender','photo_url','location', 'height','bio','interests','hobbies'
        ]

class MatchSerializer(serializers.ModelSerializer):
    matched_at = serializers.DateTimeField()

    class Meta:
        model  = Connection
        fields = ['user', 'matched_at']
