from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
#from accounts.models import Account
from users.models import UserProfile
from .models import Account, Transaction, TransferDestination


@login_required
def make_transaction(request):
    user_accounts = Account.objects.filter(user=request.user)

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    frequent_destinations = TransferDestination.objects.filter(
        user_profile=user_profile)

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
            return render(request, 'make_transaction.html', {'error_message': 'Receiver account not found', 'user_accounts': user_accounts})

        try:
            Transaction.make_transaction(
                sender_account, receiver_account, amount)
        except ValueError as e:
            return render(request, 'make_transaction.html', {'error_message': str(e), 'user_accounts': user_accounts})

        return redirect('transaction_success', receiver_account_number=receiver_account_number)

    return render(request, 'make_transaction.html', {'user_accounts': user_accounts, 'frequent_destinations': frequent_destinations})


@login_required
def save_frequent_destination(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        destination_account_number = request.POST.get(
            'destination_account_number')
        TransferDestination.save_to_frequent_transfer(
            user_profile, destination_account_number)

        return redirect('frequent_destinations')

    return render(request, 'save_frequent_destination.html')


def delete_frequent_destination(request, destination_id):
    destination = get_object_or_404(TransferDestination, pk=destination_id)

    if destination.user_profile.user != request.user:
        ########################
        pass

    destination.delete()

    return redirect('account_details')


@login_required
def transaction_history(request, account_id):
    user_accounts = Account.objects.filter(user=request.user)
    user_account = get_object_or_404(Account, pk=account_id, user=request.user)
    transactions = Transaction.objects.filter(
        sender=user_account) | Transaction.objects.filter(receiver=user_account).order_by('-timestamp')
    return render(request, 'transaction_history.html', {'user_accounts': user_accounts, 'transactions': transactions})


def transaction_success(request, receiver_account_number):
    context = {'receiver_account_number': receiver_account_number}
    return render(request, 'transaction_success.html', context)
