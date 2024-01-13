# users/management/commands/create_user_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile instances for existing users.'

    def handle(self, *args, **options):
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'UserProfile created for user: {user.username}'))
