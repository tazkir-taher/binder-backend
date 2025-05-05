from rest_framework import serializers
from authentication.models import Dater
from django.contrib.auth.password_validation import validate_password
from .models import (
    Profile, InterestCategory, UserInterest,
    ProfileQuality, UserQuality, HopingFor
)

class InterestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestCategory
        fields = ['id', 'name', 'category']

class UserInterestSerializer(serializers.ModelSerializer):
    interest = InterestCategorySerializer(read_only=True)
    interest_id = serializers.PrimaryKeyRelatedField(
        queryset=InterestCategory.objects.all(),
        source='interest', write_only=True
    )

    class Meta:
        model = UserInterest
        fields = ['interest', 'interest_id', 'created_at']

class ProfileQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileQuality
        fields = ['id', 'name', 'choice']

class UserQualitySerializer(serializers.ModelSerializer):
    quality = ProfileQualitySerializer(read_only=True)
    quality_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfileQuality.objects.all(),
        source='quality', write_only=True
    )

    class Meta:
        model = UserQuality
        fields = ['quality', 'quality_id']

class HopingForSerializer(serializers.ModelSerializer):
    quality = ProfileQualitySerializer(read_only=True)
    quality_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfileQuality.objects.all(),
        source='quality', write_only=True
    )

    class Meta:
        model = HopingFor
        fields = ['quality', 'quality_id']

class ProfileSerializer(serializers.ModelSerializer):
    interests = UserInterestSerializer(
        source='userinterest_set', many=True, read_only=True
    )
    qualities = UserQualitySerializer(
        source='userquality_set', many=True, read_only=True
    )
    hoping_for = HopingForSerializer(
        source='hopingfor_set', many=True, read_only=True
    )
    age = serializers.SerializerMethodField()
    gender = serializers.CharField(source='get_gender_display')
    lifestyle = serializers.CharField(source='get_lifestyle_display')
    height = serializers.CharField(source='get_height_display')
    relationship_goal = serializers.CharField(source='get_relationship_goal_display')

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'bio', 'birth_date', 'age',
            'gender', 'location', 'lifestyle', 'height',
            'qualities', 'interests', 'hoping_for',
            'relationship_goal'
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

    def validate(self, data):
        if 'userinterest_set' in data and len(data['userinterest_set']) > 5:
            raise serializers.ValidationError("Choose up to 5 interests.")
        if 'userquality_set' in data and len(data['userquality_set']) > 3:
            raise serializers.ValidationError("Choose up to 3 qualities.")
        if 'hopingfor_set' in data and len(data['hopingfor_set']) > 3:
            raise serializers.ValidationError("Choose up to 3 hoping_for.")
        return data
    
class ProfileCompletionSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords don't match")
        
        if Dater.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.email = self.validated_data['email']
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.set_password(self.validated_data['password'])
        user.profile_completed = True
        user.save()
        return user