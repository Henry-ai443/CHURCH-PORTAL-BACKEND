from django.shortcuts import render
from rest_framework.views import APIView
from .models import Announcement, Event
from .serializers import AnnouncementSerializer, RegisterSerializer, EventSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


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
        


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "id": user.id,
                "email": user.email,
                "token": token.key,
                "message": "User registered successfully"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

