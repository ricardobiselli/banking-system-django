from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, CustomUserCreationForm

"""@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        form = CustomUserCreationForm(data={'birth_date': instance.customusercreationform.birth_date})
        if form.is_valid():
            UserProfile.objects.create(
                user=instance,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                birth_date=form.cleaned_data['birth_date']
            )"""
