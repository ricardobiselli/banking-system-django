from django.contrib import admin
from .models import Account, TransferDestination

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number',) 


admin.site.register(Account, AccountAdmin) 
admin.site.register(TransferDestination)