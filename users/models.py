from django.db import models
from django.contrib.auth.models import User

#testuser test123123
#milenita mile123123
#niko_bellic niko123123

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
