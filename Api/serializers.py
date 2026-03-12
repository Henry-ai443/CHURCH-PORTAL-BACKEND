from rest_framework import serializers
from .models import YouthMessage, ChatMessage
from django.contrib.auth.models import User


class YouthMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouthMessage
        fields = [
            'id', 'user', 'title', 'message', 'submitted_at', 
            'is_anonymous', 'is_answered', 'answer', 'answered_at'
        ]
        read_only_fields = [
            'user', 'submitted_at', 'is_answered', 'answer', 'answered_at'
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'timestamp', 'username']

    def get_username(self, obj):
        return obj.user.username if obj.user else "Anonymous"


class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', "username", "email", "date_joined", "is_staff", "is_active"]