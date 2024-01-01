from django.contrib import admin
from accounts.models import Account
from accounts.models import TransferDestination

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number',) 


admin.site.register(Account, AccountAdmin) 
admin.site.register(TransferDestination)