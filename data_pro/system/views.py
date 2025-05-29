from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum

# Import models
from data_pro.models.customers import  *
from data_pro.models.visas import  *
from data_pro.models.passports import  *
from data_pro.models.invoices import  *
from data_pro.models.vehicles import  *
from data_pro.models.transports import  *
from data_pro.models.user import *

class SuperAdminPanelView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Super Admin Control Panel View"""
    template_name = 'admin/superadmin_panel.html'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # System-wide statistics
        context.update({
            'total_clients': Client.objects.filter(is_active=True).count(),
            'system_users': CustomUser.objects.count(),
            'active_customers': Customer.objects.filter(is_active=True).count(),
            'revenue_this_month': Invoice.objects.filter(
                issue_date__month=today.month,
                issue_date__year=today.year
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending_approvals': {
                'visas': Visa.objects.filter(status='pending').count(),
                'extensions': PassportExtension.objects.filter(released_date__isnull=True).count(),
            },
            'system_health': {
                'active_transports': Transport.objects.filter(
                    status__in=['scheduled', 'in_progress']
                ).count(),
                'available_vehicles': Vehicle.objects.filter(status='available').count(),
            }
        })
        return context

class SystemSettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """System Configuration View"""
    template_name = 'admin/system_settings.html'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add configuration options here
        context['settings_sections'] = [
            {'name': 'General', 'icon': 'bi-gear'},
            {'name': 'User Management', 'icon': 'bi-people'},
            {'name': 'Billing', 'icon': 'bi-credit-card'},
            {'name': 'Notifications', 'icon': 'bi-bell'},
        ]
        return context

class SystemDashboardView(LoginRequiredMixin, TemplateView):
    """Main system dashboard view showing key metrics"""
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # Base filter for client-specific data
        client_filter = {}
        if not (user.is_superuser or user.user_type == 'SUPERADMIN'):
            client_filter = {'client': user.client}

        # Get counts for all metrics
        context.update({
            'customer_count': Customer.objects.filter(**client_filter).count(),
            'active_visa_count': Visa.objects.filter(
                status='approved',
                **client_filter
            ).count(),
            'expiring_passports': Passport.objects.filter(
                expiry_date__range=(today, today + timezone.timedelta(days=30)),
                **client_filter
            ).exclude(status='expired').count(),
            'pending_extensions': PassportExtension.objects.filter(
                released_date__isnull=True,
                **client_filter
            ).count(),
            'available_vehicles': Vehicle.objects.filter(
                status='available',
                **client_filter
            ).count(),
            'active_transports': Transport.objects.filter(
                status__in=['scheduled', 'in_progress'],
                **client_filter
            ).count(),
            'recent_invoices': Invoice.objects.filter(
                **client_filter
            ).order_by('-issue_date')[:5],
        })
        return context

class PassportExtensionListView(LoginRequiredMixin, ListView):
    """List view for passport extensions"""
    model = PassportExtension
    template_name = 'admin/passports/extension_list.html'
    context_object_name = 'extensions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'):
            queryset = queryset.filter(
                passport__customer__client=self.request.user.client
            )
        return queryset.select_related('passport', 'handed_by')

class TransportListView(LoginRequiredMixin, ListView):
    """List view for transports with status filtering"""
    model = Transport
    template_name = 'admin/transports/list.html'
    context_object_name = 'transports'
    paginate_by = 20

    def get_queryset(self):
        status = self.request.GET.get('status', 'all')
        queryset = super().get_queryset()
        
        if status != 'all':
            queryset = queryset.filter(status=status)
        
        if not (self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'):
            queryset = queryset.filter(client=self.request.user.client)
            
        return queryset.select_related('vehicle', 'customer')

class ClientDashboardView(LoginRequiredMixin, TemplateView):
    """Client-specific dashboard view"""
    template_name = 'admin/client_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self.request.user, 'client'):
            return context
            
        client = self.request.user.client
        
        context.update({
            'client': client,
            'active_customers': Customer.objects.filter(
                client=client,
                is_active=True
            ).count(),
            'pending_visas': Visa.objects.filter(
                customer__client=client,
                status='pending'
            ).count(),
            'active_transports': Transport.objects.filter(
                client=client,
                status__in=['scheduled', 'in_progress']
            ).count(),
        })
        return context