from rest_framework import serializers
from authentication.models import Dater
from .models import Connection
from user_profile.serializers import ProfileSerializer

class FeedUserSerializer(serializers.ModelSerializer):
    age       = serializers.IntegerField()
    photo_url = serializers.SerializerMethodField()
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

    def get_photo_url(self, obj):
        request = self.context.get('request')
        photo = getattr(obj.profile, 'photo', None)
        if photo and hasattr(photo, 'url'):
            return request.build_absolute_uri(photo.url)
        return None

class MatchSerializer(serializers.ModelSerializer):
    user       = serializers.SerializerMethodField()
    matched_at = serializers.DateTimeField()

    class Meta:
        model  = Connection
        fields = ['user','matched_at']

    def get_user(self, conn):
        me    = self.context['request'].user
        other = conn.user2 if conn.user1 == me else conn.user1
        return FeedUserSerializer(other, context=self.context).data
