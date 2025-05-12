from rest_framework import serializers
from .models import Message
from authentication.models import Dater

class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dater
        fields = ['id', 'username', 'first_name', 'last_name']

class MessageSerializer(serializers.ModelSerializer):
    sender    = UserCardSerializer(read_only=True)
    recipient = UserCardSerializer(read_only=True)

    class Meta:
        model  = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'read']

class ChatPreviewSerializer(serializers.ModelSerializer):
    user            = serializers.SerializerMethodField()
    is_sent_by_user = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['user', 'content', 'timestamp', 'is_sent_by_user', 'read']

    def get_user(self, obj):
        me = self.context['request'].user
        other = obj.recipient if obj.sender == me else obj.sender
        return UserCardSerializer(other).data

    def get_is_sent_by_user(self, obj):
        return obj.sender == self.context['request'].user
