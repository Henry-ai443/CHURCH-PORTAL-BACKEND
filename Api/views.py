from django.shortcuts import render
from rest_framework.views import APIView
from .models import Announcement, Event
from .serializers import AnnouncementSerializer, EventSerializer
from rest_framework.response import Response
from rest_framework import status

class AnnouncementListApiView(APIView):
    def get(self, request):
        announcements = Announcement.objects.all().order_by('-created_at')[:3] # latest 3
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

class AllAnnouncementsView(APIView):
    def get(self, request):
        announcements = Announcement.objects.order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

#LIST ALL EVENTS
class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all().order_by('-date_time') #latest first
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#SINGLE EVENT DETAIL
class EventDetailView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error':"Event not Found"}, status=status.HTTP_404_NOT_FOUND)