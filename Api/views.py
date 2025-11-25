from django.shortcuts import render
from rest_framework.views import APIView
from .models import Announcement, Event, Profile, YouthMessage, ChatMessage
from .serializers import AnnouncementSerializer, RegisterSerializer, EventSerializer, ProfileSerializer, YouthMessageSerializer, ChatMessageSerializer, MembersSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from django.http import JsonResponse   
from django.core.mail import send_mail  
from django.conf import settings
from django.utils.timezone import now   
from django.core.mail import EmailMessage
from rest_framework.pagination import PageNumberPagination
import resend
import logging
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
import requests


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            # You can also include groups if needed later
        })


class IsStaffUser(BasePermission):

    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)



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

    def post(sself, request):
        serializer = AnnouncementSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Resposne({
                message:"Announcement added successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Resposne(serializer.errors)



class EventListView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsStaffUser()]
        return [IsAuthenticated()]

    def get(self, request):
        events = Event.objects.all().order_by('-date_time')
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#SINGLE EVENT DETAIL

class EventDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsStaffUser()]  # Only staff can modify
        return [IsAuthenticated()]  # Any authenticated user can view

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(instance=event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "The event was updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(instance=event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "The event was partially updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response({"message": "The event was deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)  # Make sure logging is set up

class YouthMessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = YouthMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(user=request.user)

            subject = f"Youth Message from {'Anonymous' if message.is_anonymous else request.user.username}"
            body_text = (
                f"Title: {message.title}\n\n"
                f"Message: {message.message}\n\n"
                f"Date: {message.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"From: {'Anonymous' if message.is_anonymous else request.user.email}"
            )

            body_html = f"""
                <h3>{message.title}</h3>
                <p>{message.message}</p>
                <p><strong>Date:</strong> {message.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>From:</strong> {'Anonymous' if message.is_anonymous else request.user.email}</p>
            """

            try:
                # Set Resend API key
                resend.api_key = settings.RESEND_API_KEY

                # Send email using Resend
                resend.Emails.send({
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": ["henrymaina2024@outlook.com"],
                    "bcc": [request.user.email] if not message.is_anonymous else [],
                    "subject": subject,
                    "text": body_text,
                    "html": body_html,
                })

                return Response({'detail': 'Message submitted and email sent successfully.'}, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error sending email with Resend API: {e}")
                return Response({'detail': 'Message submitted but failed to send email.'}, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SixPerPagePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'  # Optional: allows clients to override page size
    max_page_size = 50

class YouthAnsweredMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = SixPerPagePagination

    def get(self, request):
        messages = YouthMessage.objects.filter(is_answered=True).order_by('-answered_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        serializer = YouthMessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class YouthUnansweredMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = SixPerPagePagination

    def get(self, request):
        messages = YouthMessage.objects.filter(is_answered=False).order_by('-submitted_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        serializer = YouthMessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)



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
                "is_staff":user.is_staff,
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

class ChatMessageAPIVIEW(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = ChatMessage.objects.order_by('-timestamp')[:50]
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)





class RegisteredMembers(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Get query parameters
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        search_query = request.query_params.get('search', '')

        # Filter queryset
        users = User.objects.all().order_by('-date_joined')
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Paginate queryset
        paginator = Paginator(users, limit)
        current_page = paginator.get_page(page)
        serializer = MembersSerializer(current_page, many=True)

        # Return paginated response
        return Response({
            "users": serializer.data,
            "page": page,
            "total_pages": paginator.num_pages,
            "total_users": paginator.count,
            "has_next": current_page.has_next()
        })


"""ADMIN VIEWS"""


class AdminAnnouncementView(APIView):
    permission_classes=[IsAdminUser, IsAuthenticated]
    def get(self, request):
        announcements = Announcement.objects.all()
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Announcement created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminAnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data)

    def put(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        serializer = AnnouncementSerializer(instance=announcement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Announcenement updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        serializer = AnnouncementSerializer(instance=announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Announcenement updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.delete()
        return Response({"message":"Announcement deleted successfully"}, status=status.HTTP_404_NOT_FOUND)

class AdminEventView(APIView):

    permission_classes = [IsAdminUser, IsAuthenticated]
    def get(self, request):
        events = Event.objects.all().order_by('-date_time')
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AdminEventDetailView(APIView):
    permission_classes=[IsAdminUser, IsAuthenticated]
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(instance=event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "The event was updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(instance=event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "The event was partially updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response({"message": "The event was deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#YOUTH QUIZESS SECTION

class FetchQuizAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):

        url = "https://opentdb.com/api.php?amount=1000&category=20&type=multiple"

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("response_code") != 0:
                return Response({"error": "No questions available"}, status=status.HTTP_404_NOT_FOUND)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
