from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Announcement
from .serializers import AnnouncementSerializer


class IsStaffUser(IsAdminUser):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


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

    def post(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Announcement added successfully"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class AdminAnnouncementView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request):
        announcements = Announcement.objects.all()
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Announcement created successfully"}, status=status.HTTP_201_CREATED)
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
            return Response({"message": "Announcement updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        serializer = AnnouncementSerializer(instance=announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Announcement updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.delete()
        return Response({"message": "Announcement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
