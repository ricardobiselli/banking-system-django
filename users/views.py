from django.shortcuts import render, redirect

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