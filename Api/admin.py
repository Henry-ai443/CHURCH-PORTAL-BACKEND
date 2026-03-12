from django.contrib import admin
from django import forms
from cloudinary.forms import CloudinaryFileField
from announcements.models import Announcement
from events.models import Event
from authentication.models import Profile

class ProfileAdminForm(forms.ModelForm):
    profile_picture = CloudinaryFileField(
        options = { 'folder': 'profiles' },  # optional: set your folder on Cloudinary
        required=False,
    )

    class Meta:
        model = Profile
        fields = '__all__'

class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

admin.site.register(Announcement)
admin.site.register(Event)
admin.site.register(Profile, ProfileAdmin)
