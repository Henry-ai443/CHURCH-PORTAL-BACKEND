from django.db import models

# Create your models here.
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    entry = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title