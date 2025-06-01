from rest_framework import serializers
from .models import *

class ConnectionSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = Connection
        fields = ['id', 'sender', 'receiver', 'matched']
        read_only_fields = ['id', 'matched']