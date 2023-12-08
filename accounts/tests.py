from django.test import TestCase

from django.contrib.auth.models import User
from .models import TransferDestination, UserProfile

user = User.objects.get(username='<martincito>')
user_profile = UserProfile.objects.get(user=user)
transfer_destinations = TransferDestination.objects.filter(user_profile=user_profile)

for destination in transfer_destinations:
    print(destination.destination_account_number, destination.nickname)
