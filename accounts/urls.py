from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account_details, name='account_details'),
    path('transactionhistory/', views.transaction_history, name='transaction_history'),
    path('logout/', views.logout_view, name='logout'), 
    path('transaction/', views.make_transaction, name='transaction'),
]
