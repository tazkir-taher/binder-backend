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
    class Meta:
        model  = Message
        fields = ['content', 'timestamp', 'read']
