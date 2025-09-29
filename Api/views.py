from django.shortcuts import render
from rest_framework.views import APIView
from .models import Announcement, Event, Profile
from .serializers import AnnouncementSerializer, RegisterSerializer, EventSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse        

def root_view(request):
    return JsonResponse({"message": "Welcome to the Church Portal API"})

class AnnouncementListApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        announcements = Announcement.objects.all().order_by('-created_at')[:3] 
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

class AllAnnouncementsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        announcements = Announcement.objects.order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

#LIST ALL EVENTS
class EventListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        events = Event.objects.all().order_by('-date_time') #latest first
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#SINGLE EVENT DETAIL
class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error':"Event not Found"}, status=status.HTTP_404_NOT_FOUND)
        


class RegisterView(APIView):
    permission_classes=[AllowAny]
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


class LoginView(APIView):
    permission_classes=[AllowAny]   
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Authenticate user now
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Incorrect password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "username": user.username,
                "token": token.key,
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
