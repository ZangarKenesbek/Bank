from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, Transaction


class CustomUserAdmin(UserAdmin):
    model = UserAccount
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'balance')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('balance',)}),
    )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('sender__username', 'receiver__username')


admin.site.register(UserAccount, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
