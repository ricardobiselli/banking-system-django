from djmoney.money import Money
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Transaction, TransferDestination
from django.db import transaction
from django.db.models.signals import post_save
from decimal import Decimal, InvalidOperation
from django.dispatch import receiver
import http.client
import json
import random
from .models import Account
from django.conf import settings
from users.models import UserProfile

# milena mile123123 lucia lucia123123


from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('open_new_account')
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

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


@login_required
def transaction_history(request, account_id):
    user_accounts = Account.objects.filter(user=request.user)
    user_account = get_object_or_404(Account, pk=account_id, user=request.user)
    transactions = Transaction.objects.filter(
        sender=user_account) | Transaction.objects.filter(receiver=user_account)
    return render(request, 'transaction_history.html', {'user_accounts': user_accounts, 'transactions': transactions})





def get_exchange_rate(base_currency, target_currency):
    conn = http.client.HTTPSConnection("api.fxratesapi.com")
    conn.request("GET", f"/latest?base={base_currency}")
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        exchange_rates = json.loads(data)
        rates = exchange_rates["rates"]
        # Default to 1 if target currency not found
        return Decimal(rates.get(target_currency, 1))
    else:
        return Decimal(1)  # Default exchange rate of 1 if API request fails

    conn.close()


@login_required
def make_transaction(request):
    user_accounts = Account.objects.filter(user=request.user)

    if request.method == 'POST':
        sender_account_number = request.POST.get('sender_account')
        receiver_account_number = request.POST.get('receiver_account_number')
        amount = request.POST.get('amount')

        try:
            sender_account = Account.objects.get(
                account_number=sender_account_number, user=request.user)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Sender account not found'})

        try:
            receiver_account = Account.objects.get(
                account_number=receiver_account_number)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Receiver account not found'})

        if sender_account.currency != receiver_account.currency:
            exchange_rate = get_exchange_rate(
                sender_account.currency, receiver_account.currency)

            if exchange_rate is None:
                return render(request, 'make_transaction.html', {'error_message': 'Failed to fetch exchange rates.'})

            try:
                converted_amount = Decimal(amount) * exchange_rate
            except (InvalidOperation, TypeError, ValueError):
                return render(request, 'make_transaction.html', {'error_message': 'Invalid amount or conversion.'})

            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    sender=sender_account, receiver=receiver_account, amount=converted_amount)

                sender_account_balance = sender_account.balance
                amount_money = Money(amount, sender_account_balance.currency)
                if amount_money.amount < Decimal('0.1'):
                    return render(request, 'make_transaction.html', {'error_message': 'Invalid amount'})
                elif sender_account_balance < amount_money:
                    return render(request, 'make_transaction.html', {'error_message': 'Insufficient balance.'})
                # error messages working, empty dropdown menu after failed transaction
                sender_account.balance -= amount_money
                receiver_account.balance += Money(
                    converted_amount, receiver_account.balance.currency)

                sender_account.save()
                receiver_account.save()

                return render(request, 'transaction_success.html', {'receiver_account_number': receiver_account_number})

        else:
            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    sender=sender_account, receiver=receiver_account, amount=amount)

                sender_account_balance = sender_account.balance
                amount_money = Money(amount, sender_account_balance.currency)

                if sender_account_balance < amount_money:
                    return render(request, 'make_transaction.html', {'error_message': 'Insufficient balance.'})

                sender_account.balance -= amount_money
                receiver_account.balance += amount_money

                sender_account.save()
                receiver_account.save()

                return render(request, 'transaction_success.html', {'receiver_account_number': receiver_account_number})

    return render(request, 'make_transaction.html', {'user_accounts': user_accounts})


def save_frequent_destination_prompt(request):

    user_accounts = Account.objects.filter(user=request.user)
    if request.method == 'POST':
        receiver_account_number = request.POST.get('receiver_account_number')
        nickname = request.POST.get('nickname')

        user_profile = UserProfile.objects.get(user=request.user)

        existing_destination = TransferDestination.objects.filter(
            user_profile=user_profile,
            destination_account_number=receiver_account_number
        ).exists()

        if not existing_destination:
            TransferDestination.objects.create(
                user_profile=user_profile,
                destination_account_number=receiver_account_number,
                nickname=nickname
            )
            context = {
                'message': 'Frequent destination saved successfully.'
            }
        else:
            context = {
                'message': 'Frequent destination already exists.'
            }
        context['user_accounts'] = user_accounts
        return render(request, 'frequent_destination_saved_successfuly.html', context)

    return render(request, 'error_page.html')


def delete_frequent_destination(request, destination_id):
    destination = get_object_or_404(TransferDestination, pk=destination_id)

    if destination.user_profile.user != request.user:
        # ?????
        pass

    destination.delete()

    return redirect('account_details')

###############





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
            balance=0.00,
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
