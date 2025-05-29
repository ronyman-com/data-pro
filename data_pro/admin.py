from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# Import models using get_user_model() and proper relative imports
from django.contrib.auth import get_user_model
from .models.clients import Client
from .models.invoices import Invoice
from .models.transports import Transport
from .models.customers import Customer
from .models.vehicles import Vehicle
from .models.visas import Visa
from .models.passports import Passport

User = get_user_model()

class CustomAdminSite(admin.AdminSite):
    site_header = 'Data-Pro Administration'
    site_title = 'Data-Pro Admin'
    index_title = 'Dashboard'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        from django.shortcuts import render
        context = {
            **self.each_context(request),
            'title': 'Dashboard',
            'clients_count': Client.objects.count(),
            'customers_count': Customer.objects.count(),
            'invoices_count': Invoice.objects.count(),
        }
        return render(request, 'admin/dashboard.html', context)

admin_site = CustomAdminSite(name='system_admin')

# Client Admin
@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_email', 'contact_phone')
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['activate_clients', 'deactivate_clients']
    
    fieldsets = (
        (None, {'fields': ('name', 'contact_email', 'contact_phone')}),
        ('Status', {'fields': ('is_active',)}),
        ('Additional Info', {'fields': ('address', 'notes')}),
    )
    
    def activate_clients(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} clients were successfully activated.'), messages.SUCCESS)
    
    def deactivate_clients(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} clients were successfully deactivated.'), messages.SUCCESS)

# Custom User Admin
@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'client', 'is_active')
    list_filter = ('user_type', 'client', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 25
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Custom Fields'), {
            'fields': ('user_type', 'client')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user.client)

# Customer Admin
@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'client', 'status')
    list_filter = ('status', 'client', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_per_page = 25
    date_hierarchy = 'created_at'
    raw_id_fields = ('client',)
    
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Address'), {'fields': ('address', 'city', 'country')}),
        (_('Status'), {'fields': ('status', 'client')}),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = _('Full Name')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user.client)

# Group Admin
@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    list_per_page = 25

# Invoice Admin
@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'customer', 'total_amount', 'status', 'issue_date')
    list_filter = ('status', 'client', 'issue_date')
    search_fields = ('invoice_number', 'customer__first_name', 'customer__last_name')
    list_per_page = 25
    date_hierarchy = 'issue_date'
    raw_id_fields = ('client', 'customer')
    
    fieldsets = (
        (None, {'fields': ('invoice_number', 'client', 'customer')}),
        (_('Dates'), {'fields': ('issue_date', 'due_date')}),
        (_('Amounts'), {'fields': ('amount', 'tax', 'discount', 'total_amount')}),
        (_('Status'), {'fields': ('status', 'notes')}),
    )

# Register other models
@admin.register(Vehicle, site=admin_site)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make_model', 'license_plate', 'vehicle_type', 'status')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('make', 'model', 'license_plate')

@admin.register(Transport, site=admin_site)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle', 'status')
    list_filter = ('status', 'pickup_time')
    raw_id_fields = ('customer', 'vehicle')

@admin.register(Visa, site=admin_site)
class VisaAdmin(admin.ModelAdmin):
    list_display = ('customer', 'visa_type', 'country', 'status')
    list_filter = ('visa_type', 'country', 'status')

@admin.register(Passport, site=admin_site)
class PassportAdmin(admin.ModelAdmin):
    list_display = ('customer', 'passport_number', 'expiry_date')
    list_filter = ('expiry_date',)
    search_fields = ('passport_number', 'customer__first_name', 'customer__last_name')