from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from .utils import generate_unique_id

@receiver(post_save, sender=Profile)
def assign_unique_id_on_profile_creation(sender, instance, created, **kwargs):
    if created and instance.country and not instance.unique_id:
        country_code = instance.country[:2].upper()  # Take first 2 letters of country
        unique_id = generate_unique_id(country_code)
        
        # Ensure uniqueness
        while Profile.objects.filter(unique_id=unique_id).exists():
            unique_id = generate_unique_id(country_code)

        instance.unique_id = unique_id
        instance.save()
