# data_pro/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

# Import models
from data_pro.models.clients import Client
from data_pro.models.customers import Customer
from data_pro.models.visas import Visa
from data_pro.models.passports import Passport
from data_pro.models.invoices import Invoice
from data_pro.models.vehicles import Vehicle
from data_pro.models.transports import TransportService
from data_pro.models.AdminAuditLog import AdminAuditLog

class CustomAdminSite(admin.AdminSite):
    site_header = 'Data-Pro Administration'
    site_title = 'Data-Pro Admin Portal'
    index_title = 'System Dashboard'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('recent-activity/', self.admin_view(self.activity_view), name='recent-activity'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'System Analytics',
            'stats': {
                'clients': Client.objects.count(),
                'customers': Customer.objects.count(),
                'invoices': Invoice.objects.filter(status='pending').count(),
            }
        }
        return render(request, 'admin/analytics.html', context)
    
    def activity_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Recent Activity',
            'logs': AdminAuditLog.objects.all().order_by('-timestamp')[:50]
        }
        return render(request, 'admin/activity_log.html', context)

admin_site = CustomAdminSite(name='system_admin')

class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Client Profile'
    fields = ('company_name', 'contact_person', 'email', 'phone', 'status')
    extra = 0

class CustomerInline(admin.StackedInline):
    model = Customer
    extra = 0
    verbose_name_plural = 'Customer Profiles'
    fields = ('first_name', 'last_name', 'email', 'phone', 'status')

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_client_profile')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_client_profile(self, obj):
        if hasattr(obj, 'client_profile'):
            url = reverse('system_admin:data_pro_client_change', args=[obj.client_profile.id])
            return format_html('<a href="{}">{}</a>', url, obj.client_profile.company_name)
        return "-"
    get_client_profile.short_description = 'Client Profile'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return [ClientInline(self.model, self.admin_site), CustomerInline(self.model, self.admin_site)]

@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('company_name', 'contact_person', 'email', 'phone')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'company_name', 'contact_person')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'client', 'status')
    list_filter = ('status', 'client')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    raw_id_fields = ('user', 'client')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Organization', {
            'fields': ('client', 'user')
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_link', 'amount', 'issue_date')
    list_filter = ('issue_date',)
    search_fields = ('invoice_number', 'customer__first_name', 'customer__last_name')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(TransportService, site=admin_site)
class TransportServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'origin', 'destination', 'status')
    list_filter = ('status',)
    search_fields = ('customer__first_name', 'customer__last_name', 'origin')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(Vehicle, site=admin_site)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'license_plate', 'year')
    search_fields = ('make', 'model', 'license_plate')

@admin.register(Visa, site=admin_site)
class VisaAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_link', 'country')
    search_fields = ('country', 'customer__first_name')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(Passport, site=admin_site)
class PassportAdmin(admin.ModelAdmin):
    list_display = ('passport_number', 'customer_link', 'expiry_date')
    search_fields = ('passport_number', 'customer__first_name')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(AdminAuditLog, site=admin_site)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('admin__username', 'action')
    
    def admin_user(self, obj):
        return obj.admin.username if obj.admin else '-'
    admin_user.short_description = 'Admin User'

@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

# Unregister and re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site = admin_site
admin.sites.site = admin_site