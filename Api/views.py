from django.shortcuts import render
from rest_framework.views import APIView
from .models import YouthMessage, ChatMessage
from .serializers import YouthMessageSerializer, ChatMessageSerializer, MembersSerializer
from rest_framework.response import Response
from rest_framework import status
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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


def root_view(request):
    return JsonResponse({"message": "Welcome to the Church Portal API"})


logger = logging.getLogger(__name__)


class SixPerPagePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'  # Optional: allows clients to override page size
    max_page_size = 50


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


class FetchQuizAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Categories to fetch: Mythology (20) as religion proxy + other categories
        categories = [20, 9, 17, 23, 21]  # Mythology, General, Science, History, Sports
        all_questions = []

        try:
            for cat in categories:
                url = f"https://opentdb.com/api.php?amount=200&category={cat}&type=multiple"
                response = requests.get(url)
                data = response.json()

                if data.get("response_code") == 0:
                    all_questions.extend(data["results"])

            if not all_questions:
                return Response({"error": "No questions available"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"results": all_questions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DailyVerseAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
   
            url = "https://labs.bible.org/api/?type=json&passage=random"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return Response(
                    {"error": "Bible API is unavailable."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            data = response.json()

            # The external API returns a list of one verse
            verse = data[0] if isinstance(data, list) and data else data

            return Response({
                "book": verse.get("bookname"),
                "chapter": verse.get("chapter"),
                "verse": verse.get("verse"),
                "text": verse.get("text")
            })

        except Exception as e:
            return Response(
                {"error": "Failed to fetch verse."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
