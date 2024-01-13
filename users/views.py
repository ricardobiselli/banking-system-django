from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import CustomUserCreationForm #move to forms
    
def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid. Data:", form.cleaned_data)
            user = form.save()
            print("User object created:", user)
            login(request, user)
            return redirect('open_new_account')
        else:
            print("Form is not valid. Errors:", form.errors)
    return render(request, 'register.html', {'form': form})

    

def logout_view(request):
    logout(request)
    return redirect('login')

