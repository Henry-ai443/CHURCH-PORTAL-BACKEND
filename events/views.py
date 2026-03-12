from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from django.shortcuts import get_object_or_404
from .models import Event
from .serializers import EventSerializer


class IsStaffUser(BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


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
    permission_classes = [IsAdminUser, IsAuthenticated]

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
