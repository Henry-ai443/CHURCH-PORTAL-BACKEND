from django.shortcuts import render
from rest_framework.views import APIView
from .models import Announcement, Event, Profile, YouthMessage
from .serializers import AnnouncementSerializer, RegisterSerializer, EventSerializer, ProfileSerializer, YouthMessageSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.http import JsonResponse   
from django.core.mail import send_mail  
from django.conf import settings
from django.utils.timezone import now   
from django.core.mail import EmailMessage



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
        

class YouthMessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = YouthMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(user=request.user)
            subject = f"Youth Message from {'Anonymous' if message.is_anonymous else request.user.username}"
            body = (
                f"Title: {message.title}\n\n"
                f"Message: {message.message}\n\n"
                f"Date: {message.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"From: {'Anonymous' if message.is_anonymous else request.user.email}"
            )

            try:
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=['henrymaina2024@outlook.com'],
                    bcc=[request.user.email] if not message.is_anonymous else [],
                )
                email.send(fail_silently=False)
                return Response({'detail': 'Message submitted and email sent successfully.'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YouthAnsweredMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = YouthMessage.objects.filter(is_answered=True).order_by('-answered_at')
        serializer = YouthMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class YouthUnansweredMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = YouthMessage.objects.filter(is_answered=False).order_by('-submitted_at')
        serializer = YouthMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class YouthMessageAnswerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            message = YouthMessage.objects.get(pk=pk)
        except YouthMessage.DoesNotExist:
            return Response({'detail': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)
        answer = request.data.get('answer')
        if not answer:
            return Response({'detail': 'Answer is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        
        message.answer = answer
        message.is_answered = True
        message.answered_at = now()
        message.save()

        return Response({'detail': 'Message answered successfully.'}, status=status.HTTP_200_OK)

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

        print("PATCH request data:", request.data)  # What data was sent?

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            print("Serializer validated data:", serializer.validated_data)
            serializer.save()
            print("Updated profile:", serializer.data)
            return Response(serializer.data)
        else:
            print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password:
            return Response({"detail": "New password cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
