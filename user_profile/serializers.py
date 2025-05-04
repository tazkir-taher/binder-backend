from rest_framework import serializers
from .models import Profile, InterestCategory, UserInterest

class InterestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestCategory
        fields = ['id', 'name', 'category']

class UserInterestSerializer(serializers.ModelSerializer):
    interest = InterestCategorySerializer(read_only=True)
    interest_id = serializers.PrimaryKeyRelatedField(
        queryset=InterestCategory.objects.all(),
        source='interest',
        write_only=True
    )

    class Meta:
        model = UserInterest
        fields = ['interest', 'interest_id', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    interests = UserInterestSerializer(
        source='userinterest_set',
        many=True,
        read_only=True
    )
    age = serializers.SerializerMethodField()
    zodiac_sign = serializers.CharField(source='get_zodiac_sign_display')
    mbti = serializers.CharField(source='get_mbti_display')
    dietary_preference = serializers.CharField(source='get_dietary_preference_display')

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'bio', 'birth_date', 'age',
            'gender', 'location', 'zodiac_sign', 'mbti',
            'dietary_preference', 'interests'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def get_age(self, obj):
        from datetime import date
        if obj.birth_date:
            today = date.today()
            return today.year - obj.birth_date.year - (
                (today.month, today.day) < 
                (obj.birth_date.month, obj.birth_date.day)
            )
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['gender'] = instance.get_gender_display()
        return data