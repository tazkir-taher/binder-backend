from rest_framework import serializers
from .models import Dater

class DaterRegistrationSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8, label="Confirm password")

    class Meta:
        model  = Dater
        fields = [
            'first_name', 'last_name',
            'email', 'birth_date', 'gender',
            'password', 'password2',
        ]


class DaterSerializer(serializers.ModelSerializer):
    interests = serializers.ListField(child=serializers.ChoiceField(choices=Dater.INTERESTS),write_only=True,required=False)
    interests_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Dater
        fields = [
            'id', 'first_name', 'last_name',
            'email', 'birth_date', 'gender', 'age',
            'location', 'height', 'bio',
            'interests', 'interests_list', 'hobbies',
            'mandatory_image', 'optional_image1',
            'optional_image2', 'optional_image3'
        ]
        read_only_fields = ['id', 'email', 'age', 'gender', 'birth_date']

    def get_interests_list(self, instance):
        raw = instance.interests
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str) and raw:
            return [i.strip() for i in raw.split(',') if i.strip()]
        return []

    def update(self, instance, validated_data):
        interests_in = validated_data.pop('interests', None)
        if interests_in is not None:
            instance.interests = ','.join(interests_in)
        return super().update(instance, validated_data)

    def get_age(self, obj):
        return obj.age

class ChangePasswordSerializer(serializers.ModelSerializer):
    
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    class Meta:
        model = Dater
        fields = [ 'password', 'new_password1', 'new_password2']


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    class Meta:
        model = Dater
        fields = ['email', 'new_password1', 'new_password2']