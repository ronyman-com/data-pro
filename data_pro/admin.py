# data_pro/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Client

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = 'Data-Pro Administration'
    site_title = 'Data-Pro Admin'
    index_title = 'Dashboard'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('custom-view/', self.admin_view(self.custom_view), name='custom-view'),
        ]
        return custom_urls + urls
    
    def custom_view(self, request):
        from django.shortcuts import render
        context = {
            **self.each_context(request),
            'title': 'Custom Admin View',
        }
        return render(request, 'admin/custom_view.html', context)

# Create custom admin site instance
admin_site = CustomAdminSite(name='system_admin')

# Client Admin
@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'client_actions')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_per_page = 20
    actions = ['activate_clients', 'deactivate_clients']
    
    def client_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}">Delete</a>',
            reverse('system_admin:data_pro_client_change', args=[obj.id]),
            reverse('system_admin:data_pro_client_delete', args=[obj.id])
        )
    client_actions.short_description = 'Actions'
    client_actions.allow_tags = True
    
    def activate_clients(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Activated {queryset.count()} clients")
    activate_clients.short_description = "Activate selected clients"
    
    def deactivate_clients(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {queryset.count()} clients")
    deactivate_clients.short_description = "Deactivate selected clients"

# Custom User Admin
@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'client', 'is_active', 'user_actions')
    list_filter = ('user_type', 'client', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 20
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'client')
        }),
    )
    
    def user_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}">Delete</a>',
            reverse('system_admin:data_pro_user_change', args=[obj.id]),
            reverse('system_admin:data_pro_user_delete', args=[obj.id])
        )
    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.user_type == 'SUPERADMIN':
            return qs
        return qs.filter(client=request.user.client)

# Register Group model
@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)