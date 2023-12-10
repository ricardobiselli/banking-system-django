import random, decimal
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction, UserProfile, TransferDestination
from django.db import transaction
from djmoney.models.fields import MoneyField
from django.conf import settings


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

def make_transaction(request):
    if request.method == 'POST':
        sender_account = Account.objects.get(user=request.user)
        receiver_account_number = request.POST['receiver_account_number']
        amount = request.POST['amount']

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

    return render(request, 'make_transaction.html')


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

