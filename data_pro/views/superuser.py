from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from data_pro.models.customers import *
from data_pro.models.visas import *
from data_pro.models.passports import *
from data_pro.models.invoices import *
from data_pro.models.vehicles import *
from data_pro.models.transports import *
from data_pro.models.user import *



from data_pro.forms.user import CustomUserCreationForm, CustomUserChangeForm

class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only superadmins can access the view"""
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.user_type == 'SUPERADMIN'
    
    def handle_no_permission(self):
        messages.error(self.request, _("You don't have permission to access this page."))
        return super().handle_no_permission()

class SuperAdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    """Super Admin Dashboard View"""
    template_name = 'admin/superuser/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': CustomUser.objects.count(),
            'active_clients': Client.objects.filter(is_active=True).count(),
            'recent_activity': SystemLog.objects.all().order_by('-timestamp')[:10],
        })
        return context

class UserListView(SuperAdminRequiredMixin, ListView):
    """List all system users"""
    model = CustomUser
    template_name = 'admin/superuser/user_list.html'
    context_object_name = 'users'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user type if specified
        user_type = self.request.GET.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
            
        return queryset.select_related('client').order_by('-date_joined')

class UserCreateView(SuperAdminRequiredMixin, CreateView):
    """Create new system users"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'admin/superuser/user_form.html'
    success_url = reverse_lazy('superuser:user-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('User %(username)s created successfully') % {'username': self.object.username}
        )
        return response

class UserUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Update existing users"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'admin/superuser/user_form.html'
    success_url = reverse_lazy('superuser:user-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('User %(username)s updated successfully') % {'username': self.object.username}
        )
        return response

class UserDetailView(SuperAdminRequiredMixin, DetailView):
    """View user details"""
    model = CustomUser
    template_name = 'admin/superuser/user_detail.html'
    context_object_name = 'user_object'

class UserDeleteView(SuperAdminRequiredMixin, DeleteView):
    """Delete users"""
    model = CustomUser
    template_name = 'admin/superuser/user_confirm_delete.html'
    success_url = reverse_lazy('superuser:user-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            _('User %(username)s deleted successfully') % {'username': self.object.username}
        )
        return response

class ClientListView(SuperAdminRequiredMixin, ListView):
    """List all clients"""
    model = Client
    template_name = 'admin/superuser/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class ClientCreateView(SuperAdminRequiredMixin, CreateView):
    """Create new clients"""
    model = Client
    fields = ['name', 'contact_email', 'contact_phone', 'address', 'is_active']
    template_name = 'admin/superuser/client_form.html'
    success_url = reverse_lazy('superuser:client-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Client %(name)s created successfully') % {'name': self.object.name}
        )
        return response

class ClientUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Update existing clients"""
    model = Client
    fields = ['name', 'contact_email', 'contact_phone', 'address', 'is_active']
    template_name = 'admin/superuser/client_form.html'
    success_url = reverse_lazy('superuser:client-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Client %(name)s updated successfully') % {'name': self.object.name}
        )
        return response

class SystemLogsView(SuperAdminRequiredMixin, ListView):
    """View system activity logs"""
    model = SystemLog
    template_name = 'admin/superuser/system_logs.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by log type if specified
        log_type = self.request.GET.get('type')
        if log_type:
            queryset = queryset.filter(log_type=log_type)
            
        return queryset.select_related('user').order_by('-timestamp')

class SystemSettingsView(SuperAdminRequiredMixin, TemplateView):
    """System configuration view"""
    template_name = 'admin/superuser/system_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings_sections'] = [
            {'name': 'General', 'icon': 'bi-gear', 'url': 'superuser:settings-general'},
            {'name': 'Email', 'icon': 'bi-envelope', 'url': 'superuser:settings-email'},
            {'name': 'Security', 'icon': 'bi-shield-lock', 'url': 'superuser:settings-security'},
        ]
        return context