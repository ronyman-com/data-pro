from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from ..models import Customer

class CustomerAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only authorized users can access customer views"""
    
    def test_func(self):
        user = self.request.user
        # Superusers and staff can access all customers
        if user.is_superuser or user.is_staff:
            return True
        
        # Client users can only access their own customers
        if hasattr(user, 'client'):
            customer = self.get_object()
            return customer.user == user
        
        return False
    
    def handle_no_permission(self):
        raise PermissionDenied("You don't have permission to access this customer.")

class CustomerFormMixin:
    """Mixin to handle common form processing for Customer views"""
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Automatically associate the customer with the current user
        if not self.request.user.is_superuser and not self.request.user.is_staff:
            form.instance.user = self.request.user
        return super().form_valid(form)

class CustomerSuccessUrlMixin:
    """Mixin to provide success URLs for Customer views"""
    
    def get_success_url(self):
        # You can customize the success URL based on user type
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse_lazy('data_pro:customer-list')
        return reverse_lazy('data_pro:dashboard')