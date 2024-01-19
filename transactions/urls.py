from django.urls import path
from . import views


urlpatterns = [
    path('transaction_history/<int:account_id>/',
         views.transaction_history, name='transaction_history'),
    path('make_transaction/', views.make_transaction, name='make_transaction'),
    path('save_frequent_destination_prompt/', views.save_frequent_destination_prompt,
         name='save_frequent_destination_prompt'),
    path('delete_frequent_destination/<int:destination_id>/',
         views.delete_frequent_destination, name='delete_frequent_destination'),
    #path('transaction_success/', views.transaction_success, name="transaction_success"),

]
