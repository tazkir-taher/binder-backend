from rest_framework import serializers
from .models import Swipe

class SwipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Swipe
        fields = ['id', 'swiper', 'swiped', 'type', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'swiper']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['swiper'] = request.user
        return super().create(validated_data)
