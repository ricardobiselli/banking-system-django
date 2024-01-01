from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from .models import Account
from django.conf import settings
from users.models import UserProfile
from transactions.models import TransferDestination

@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@login_required
def account_details(request):
    user_accounts = Account.objects.filter(user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)
    frequent_destinations = TransferDestination.objects.filter(
        user_profile=user_profile)

    return render(request, 'account_details.html', {'user_accounts': user_accounts, 'frequent_destinations': frequent_destinations})


def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

def open_new_account(request):
    user_accounts = Account.objects.filter(user=request.user)

    currencies = settings.PRESET_CURRENCIES
    new_account_number = generate_account_number()

    if request.method == 'POST':
        selected_currency = request.POST.get('currency')
        new_account = Account.objects.create(
            user=request.user,
            balance=10000.00,
            account_number=new_account_number,
            currency=selected_currency
        )
        return render(request, 'new_account_created.html', {'new_account': new_account})

    return render(request, 'select_currency.html', {'currencies': currencies, 'user_accounts': user_accounts})

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id)

    if account.user != request.user:
        pass

    if account.balance.amount > 0:
        return render(request, 'delete_account_error.html', {'account': account})

    account.delete()

    return redirect('account_details')
