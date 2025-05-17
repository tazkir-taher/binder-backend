from rest_framework import serializers
from .models import DaterProfile

class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name  = serializers.CharField(source='user.last_name',  read_only=True)
    email      = serializers.EmailField(source='user.email',      read_only=True)
    age        = serializers.IntegerField(source='user.age',      read_only=True)
    gender     = serializers.CharField(source='user.gender',     read_only=True)
    photo_url  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = DaterProfile
        fields = [
            'first_name', 'last_name',
            'email', 'age', 'gender',
            'location', 'height', 'bio',
            'interests', 'hobbies',
            'photo_url',
        ]

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            return request.build_absolute_uri(obj.photo.url)
        return None
