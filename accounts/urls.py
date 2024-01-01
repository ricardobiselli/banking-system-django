from django.urls import path
from . import views
from django.urls import path

urlpatterns = [

    path('open_new_account', views.open_new_account, name='open_new_account'),
    path('delete_account/<int:account_id>/',
         views.delete_account, name='delete_account'),
    path('account/', views.account_details, name='account_details'),

]
