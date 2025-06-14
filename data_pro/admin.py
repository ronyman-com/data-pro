# data_pro/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

# Import models
from data_pro.models.clients import *
from data_pro.models.customers import *
from data_pro.models.visas import *
from data_pro.models.passports import *
from data_pro.models.invoices import *
from data_pro.models.vehicles import *
from data_pro.models.transports import *
from data_pro.models.AdminAuditLog import *
from data_pro.models.office import *

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
    verbose_name_plural = _('Client Account')
    fields = (
        'user_type',
        'status',
        'company_name',
        'contact_person',
        'email',
        'phone'
    )

class CustomerInline(admin.StackedInline):
    model = Customer
    extra = 0
    verbose_name_plural = _('Customer Accounts')
    fields = (
        'status',
        'first_name',
        'last_name',
        'email',
        'phone',
        'client'
    )

class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'get_user_type',
        'get_client_status',
        'is_staff',
        'get_client_account'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    def get_user_type(self, obj):
        if hasattr(obj, 'client_account'):
            return obj.client_account.get_user_type_display()
        return _("N/A")
    get_user_type.short_description = _('User Type')
    
    def get_client_status(self, obj):
        if hasattr(obj, 'client_account'):
            return obj.client_account.get_status_display()
        return _("N/A")
    get_client_status.short_description = _('Client Status')
    
    def get_client_account(self, obj):
        if hasattr(obj, 'client_account'):
            url = reverse('admin:data_pro_client_change', args=[obj.client_account.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.client_account.company_name
            )
        return "-"
    get_client_account.short_description = _('Client Organization')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'email', 'status', 'is_verified')
    list_filter = ('status', 'is_verified', 'country')
    search_fields = ('company_name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'full_address')
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'is_verified')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_reg_number', 'tax_id')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'email', 'phone', 'alternate_phone', 'website')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'client', 'status', 'created_at')
    list_filter = ('status', 'client', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'client')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user.client)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client" and not request.user.is_superuser:
            kwargs["queryset"] = Client.objects.filter(id=request.user.client.id)
            kwargs["initial"] = request.user.client
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    list_display = ('visa_number', 'customer_link', 'issuing_country', 'status', 'expiry_date')
    list_filter = ('status', 'issuing_country')
    search_fields = ('visa_number', 'customer__first_name', 'customer__last_name', 'issuing_country')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(Passport, site=admin_site)
class PassportAdmin(admin.ModelAdmin):
    list_display = ('passport_number', 'customer_link', 'issuing_country', 'expiry_date')
    search_fields = ('passport_number', 'customer__first_name', 'customer__last_name')
    
    def customer_link(self, obj):
        url = reverse('system_admin:data_pro_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, f"{obj.customer.first_name} {obj.customer.last_name}")
    customer_link.short_description = 'Customer'

@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

@admin.register(Office, site=admin_site)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'email', 'phone')
    ordering = ('name',)

# Unregister and re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site = admin_site
admin.sites.site = admin_site