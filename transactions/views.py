from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from accounts.models import Account
from users.models import UserProfile
from djmoney.money import Money
from .models import Transaction, TransferDestination
from django.db import transaction
from decimal import Decimal, InvalidOperation
import http.client
import json
from django.urls import reverse


def get_exchange_rate(base_currency, target_currency):
    conn = http.client.HTTPSConnection("api.fxratesapi.com")
    conn.request("GET", f"/latest?base={base_currency}")
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        exchange_rates = json.loads(data)
        rates = exchange_rates["rates"]
        return Decimal(rates.get(target_currency, 1))
    else:
        return Decimal(1)

    conn.close()


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

        if sender_account.currency != receiver_account.currency:
            exchange_rate = get_exchange_rate(
                sender_account.currency, receiver_account.currency)

            if exchange_rate is None:
                return render(request, 'make_transaction.html', {'error_message': 'Failed to fetch exchange rates!', 'user_accounts': user_accounts})

            try:
                converted_amount = Decimal(amount) * exchange_rate
            except (InvalidOperation, TypeError, ValueError):
                return render(request, 'make_transaction.html', {'error_message': 'Invalid amount or conversion.', 'user_accounts': user_accounts})

            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    sender=sender_account, receiver=receiver_account, amount=converted_amount)

                sender_account_balance = sender_account.balance
                amount_money = Money(amount, sender_account_balance.currency)
                if amount_money.amount < Decimal('0.1'):
                    return render(request, 'make_transaction.html', {'error_message': 'Invalid amount', 'user_accounts': user_accounts})
                elif sender_account_balance < amount_money:
                    return render(request, 'make_transaction.html', {'error_message': 'Insufficient balance.', 'user_accounts': user_accounts})
                sender_account.balance -= amount_money
                receiver_account.balance += Money(
                    converted_amount, receiver_account.balance.currency)

                sender_account.save()
                receiver_account.save()

                return redirect('transaction_success', receiver_account_number=receiver_account_number) 

        else:
            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    sender=sender_account, receiver=receiver_account, amount=amount)

                sender_account_balance = sender_account.balance
                amount_money = Money(amount, sender_account_balance.currency)

                if sender_account_balance < amount_money:
                    return render(request, 'make_transaction.html', {'error_message': 'Insufficient balance.', 'user_accounts': user_accounts})

                sender_account.balance -= amount_money
                receiver_account.balance += amount_money

                sender_account.save()
                receiver_account.save()

                return redirect('transaction_success', receiver_account_number=receiver_account_number) 
    return render(request, 'make_transaction.html', {'user_accounts': user_accounts, 'frequent_destinations': frequent_destinations})


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
            try:
                recipient_account = Account.objects.get(
                    account_number=receiver_account_number)
                currency = recipient_account.currency

                TransferDestination.objects.create(
                    user_profile=user_profile,
                    destination_account_number=receiver_account_number,
                    nickname=nickname,
                    currency=currency
                )
                context = {'message': 'Frequent recipient saved successfully!'}
            except Account.DoesNotExist:
                context = {'message': 'Receiver account not found.'}
        else:
            context = {'message': 'Frequent recipient already exists.'}

        context['user_accounts'] = user_accounts
        return render(request, 'frequent_destination_saved_successfuly.html', context)

    return HttpResponseRedirect(reverse('make_transaction'))


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
