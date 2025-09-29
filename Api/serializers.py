from rest_framework import serializers
from .models import Announcement, Event, Profile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'time','created_at']

class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'location','image','zoom_link', 'entry']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    image = serializers.ImageField(source='profile_picture', use_url=True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'image', 'created', 'updated']
        read_only_fields = ['created', 'updated']