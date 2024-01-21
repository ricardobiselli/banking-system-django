from django.db import models
from users.models import UserProfile
from accounts.models import Account
from django.db import transaction
from decimal import Decimal, InvalidOperation
from djmoney.money import Money
from .utils import get_exchange_rate

class Transaction(models.Model):
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.user.username} sent {self.amount} to {self.receiver.user.username} on {self.timestamp}"
    
    @classmethod
    def make_transaction(cls, sender_account, receiver_account, amount):
        exchange_rate = get_exchange_rate(sender_account.currency, receiver_account.currency)

        if exchange_rate is None:
            raise ValueError('Failed to fetch exchange rates!')

        try:
            converted_amount = Decimal(amount) * exchange_rate
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError('Invalid amount or conversion.')

        with transaction.atomic():
            transaction_obj = cls.objects.create(
                sender=sender_account, receiver=receiver_account, amount=converted_amount)

            sender_account_balance = sender_account.balance
            amount_money = Money(amount, sender_account_balance.currency)
            if amount_money.amount < Decimal('0.1'):
                raise ValueError('Invalid amount')
            elif sender_account_balance < amount_money:
                raise ValueError('Insufficient balance.')

            sender_account.balance -= amount_money
            receiver_account.balance += Money(converted_amount, receiver_account.balance.currency)

            sender_account.save()
            receiver_account.save()

        return transaction_obj

class TransferDestination(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    destination_account_number = models.CharField(max_length=20)
    nickname = models.CharField(max_length=50) 
    currency = models.CharField(max_length=3, default='USD')  

    def __str__(self):
        return f"{self.destination_account_number} ({self.nickname})"
    
    @classmethod
    def save_to_frequent_transfer(cls, user_profile, destination_account_number):
        transfer_dest = cls(
            user_profile=user_profile,
            destination_account_number=destination_account_number,
        )
        transfer_dest.save()

    
def save_to_frequent_transfer(user_profile, destination_account_number):
    transfer_dest = TransferDestination(
        user_profile=user_profile,
        destination_account_number=destination_account_number,
    )
    transfer_dest.save()


