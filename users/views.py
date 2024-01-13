from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import UserProfile, CustomUserCreationForm

def register(request):
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                birth_date=form.cleaned_data['birth_date']
            )

            login(request, user)
            return redirect('open_new_account')

    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

