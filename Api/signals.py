from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .utils import generate_unique_id

@receiver(post_save, sender=User)
def assign_unique_id_on_profile_creation(sender, instance, created, **kwargs):
    if created:
        profile = instance.profile
        if profile.country and not profile.unique_id:
            unique_id = generate_unique_id(profile.country)
            while Profile.objects.filter(unique_id=unique_id).exists():
                unique_id = generate_unique_id(profile.country)
            profile.unique_id = unique_id
            profile.save()

