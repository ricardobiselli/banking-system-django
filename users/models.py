from django.db import models
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from datetime import date

#testuser test123123
#milenita mile123123
#niko_bellic niko123123

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField( max_length=50,default='')
    last_name = models.CharField(max_length=50,default='')
    birth_date = models.DateField(null=True, blank=True)
    
# move to users/forms.py
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        print(f'Cleaned birth_date: {birth_date}')  #debug

        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if age < 18:
                raise ValidationError("You must be at least 18 years old to register.")

        return birth_date

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
