from rest_framework import serializers
from .models import Announcement, Event

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'time','created_at']

class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'location','image','zoom_link', 'entry']