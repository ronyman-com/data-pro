# data_pro/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Client


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'client', 'is_active')
    list_filter = ('user_type', 'client')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'client')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superadmin():
            return qs
        return qs.filter(client=request.user.client)


admin.site.register(User, CustomUserAdmin)


    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)