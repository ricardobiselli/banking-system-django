from django.urls import path
from . import views

app_name = 'account_create_and_delete'  # Define the namespace for the 'account_create_and_delete' app

urlpatterns = [

    path('open_new_account', views.open_new_account, name='open_new_account'),
    path('delete_account/<int:account_id>/',
         views.delete_account, name='delete_account'),
]
