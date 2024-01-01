from django.db import models
from users.models import UserProfile
from accounts.models import Account

class Transaction(models.Model):
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.user.username} sent {self.amount} to {self.receiver.user.username} on {self.timestamp}"

class TransferDestination(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    destination_account_number = models.CharField(max_length=20)
    nickname = models.CharField(max_length=50) 
    currency = models.CharField(max_length=3, default='USD')  

    def __str__(self):
        return f"{self.destination_account_number} ({self.nickname})"
    
def save_to_frequent_transfer(user_profile, destination_account_number):
    transfer_dest = TransferDestination(
        user_profile=user_profile,
        destination_account_number=destination_account_number,
    )
    transfer_dest.save()


