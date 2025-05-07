from rest_framework import serializers
from authentication.models import Dater
from .models import Swipe, Match

class FeedUserSerializer(serializers.ModelSerializer):
    age       = serializers.IntegerField()
    location  = serializers.CharField(source='profile.location', read_only=True)
    height    = serializers.IntegerField(source='profile.height',    read_only=True)
    bio       = serializers.CharField(source='profile.bio',         read_only=True)
    interests = serializers.CharField(source='profile.interests',   read_only=True)
    hobbies   = serializers.CharField(source='profile.hobbies',     read_only=True)

    class Meta:
        model  = Dater
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'age', 'gender',
            'location', 'height', 'bio',
            'interests', 'hobbies'
        ]

class UserCardSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField()

    class Meta:
        model  = Dater
        fields = ['id', 'username', 'first_name', 'last_name', 'age', 'gender']

class SwipeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Swipe
        fields = ['id', 'swiped', 'liked']

class MatchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model  = Match
        fields = ['user', 'timestamp']

    def get_user(self, obj):
        request_user = self.context['request'].user
        match_user   = obj.user2 if obj.user1 == request_user else obj.user1
        return UserCardSerializer(match_user, context=self.context).data
