from rest_framework import serializers
from .models import *

class ConnectionSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = Connection
        fields = ['id', 'sender', 'receiver', 'matched']
        read_only_fields = ['id', 'matched']

class ConnectionSearchSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()

    class Meta:
        model = ConnectionSearch
        fields = ['min_age', 'max_age', 'interests', 'lock']

    def get_interests(self, obj):
        return obj.interests.split(',') if obj.interests else []