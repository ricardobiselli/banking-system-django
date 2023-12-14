import random, decimal
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction, UserProfile, TransferDestination
from django.db import transaction
from djmoney.models.fields import MoneyField
from django.conf import settings
from decimal import Decimal
import http.client
import json


#milena mile123123 lucia lucia123123

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))  

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
           
            account_number = generate_account_number()
            Account.objects.create(user=user, account_number=account_number)
            
            login(request, user)  
            return redirect('account_details') 
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def account_details(request):
    user_accounts = Account.objects.filter(user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)
    frequent_destinations = TransferDestination.objects.filter(user_profile=user_profile)
    #balance = user_accounts.balance
    
    return render(request, 'account_details.html', {'user_accounts': user_accounts, 'frequent_destinations': frequent_destinations})

def transaction_history(request):
    user_account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(sender=user_account) | Transaction.objects.filter(receiver=user_account)
    return render(request, 'transaction_history.html', {'transactions': transactions})

def logout_view(request):
    logout(request)
    return redirect('login')

def get_exchange_rate(base_currency, target_currency):
    conn = http.client.HTTPSConnection("api.fxratesapi.com")
    conn.request("GET", f"/latest?base={base_currency}")
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        exchange_rates = json.loads(data)
        rates = exchange_rates["rates"]
        return Decimal(rates.get(target_currency, 1))  # Default to 1 if target currency not found
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
            sender_account = Account.objects.get(account_number=sender_account_number, user=request.user)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Sender account not found'})

        try:
            receiver_account = Account.objects.get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Receiver account not found'})

        # Check if sender and receiver have different currencies
        if sender_account.currency != receiver_account.currency:
            exchange_rate = get_exchange_rate(sender_account.currency, receiver_account.currency)

            if exchange_rate is None:
                return render(request, 'make_transaction.html', {'error_message': 'Failed to fetch exchange rates.'})

            try:
                converted_amount = Decimal(amount) * exchange_rate
            except Decimal.InvalidOperation:
                return render(request, 'make_transaction.html', {'error_message': 'Invalid amount.'})

            # Perform the transaction with converted amount
            with transaction.atomic():
                transaction_obj = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=converted_amount)

                sender_account.balance -= Decimal(amount)
                receiver_account.balance += converted_amount

                sender_account.save()
                receiver_account.save()

                return render(request, 'transaction_success.html', {
                    'receiver_account_number': receiver_account_number
                })
                
        else:
            with transaction.atomic():
                transaction_obj = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)

                sender_account.balance -= decimal.Decimal(amount)
                receiver_account.balance += decimal.Decimal(amount)

                sender_account.save()
                receiver_account.save()

                return render(request, 'transaction_success.html', {
                    'receiver_account_number': receiver_account_number
                })

    

    return render(request, 'make_transaction.html', {'user_accounts': user_accounts})

####################################
def make_transaction(request):
    user_accounts = Account.objects.filter(user=request.user)
    
    if request.method == 'POST':
        sender_account_number = request.POST.get('sender_account')
        receiver_account_number = request.POST.get('receiver_account_number')
        amount = request.POST.get('amount')

        try:
            sender_account = Account.objects.get(account_number=sender_account_number, user=request.user)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Sender account not found'})

        try:
            receiver_account = Account.objects.get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            return render(request, 'make_transaction.html', {'error_message': 'Receiver account not found'})

        with transaction.atomic():
            transaction_obj = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)

            sender_account.balance -= decimal.Decimal(amount)
            receiver_account.balance += decimal.Decimal(amount)

            sender_account.save()
            receiver_account.save()

            return render(request, 'transaction_success.html', {
                'receiver_account_number': receiver_account_number
            })

    return render(request, 'make_transaction.html', {'user_accounts': user_accounts})
   
    


def save_frequent_destination_prompt(request):
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

        return render(request, 'frequent_destination_saved_successfuly.html', context)

    return render(request, 'error_page.html')  

def delete_frequent_destination(request, destination_id):
    destination = get_object_or_404(TransferDestination, pk=destination_id)

    if destination.user_profile.user != request.user:
        # ?????
        pass

    destination.delete()

    return redirect('account_details')

def open_secondary_account(request):
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
        return render(request, 'open_secondary_account.html', {'new_account': new_account})

    return render(request, 'select_currency.html', {'currencies': currencies})

