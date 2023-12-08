import random, decimal
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction, UserProfile, TransferDestination, save_to_frequent_transfer
from django.db import transaction


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
    user_account = Account.objects.get(user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)
    frequent_destinations = TransferDestination.objects.filter(user_profile=user_profile)
    
    return render(request, 'account_details.html', {'account': user_account, 'frequent_destinations': frequent_destinations})

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
            return render(request, 'transaction.html', {'error_message': 'Receiver account not found'})

        with transaction.atomic():
            transaction_obj = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)

            sender_account.balance -= decimal.Decimal(amount)
            receiver_account.balance += decimal.Decimal(amount)

            sender_account.save()
            receiver_account.save()
            
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            #user_profile = UserProfile.objects.get(user=request.user)
            save_to_frequent_transfer(user_profile, receiver_account_number)


        return render(request, 'transaction_success.html')
    else:
        return render(request, 'transaction.html')

def save_frequent_destination(request):
    if request.method == 'POST':
        receiver_account_number = request.POST.get('receiver_account_number')
        nickname = request.POST.get('nickname')

        # Assuming you've retrieved the user's profile here
        user_profile = UserProfile.objects.get(user=request.user)

        # Save the transaction details as a frequent destination
        TransferDestination.objects.create(
            user_profile=user_profile,
            destination_account_number=receiver_account_number,
            nickname=nickname
        )
        
        context = {
            'user_profile': user_profile,
            'destination_account_number': receiver_account_number,
            'nickname': nickname,
        }

        return render(request, 'save_frequent_destination_success.html', context)

    # Handle invalid requests or redirect to another page if needed
    return render(request, 'error_page.html')  # Replace 'error_page.html' with an appropriate error template