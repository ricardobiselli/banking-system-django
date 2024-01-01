from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

from users.models import UserProfile

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=10, decimal_places=2, default=0.00, default_currency='USD')
    account_number = models.CharField(max_length=10, unique=True)  
    currency = models.CharField(max_length=3)
    
    def __str__(self):
        return f"{self.user.username}'s account"


    
