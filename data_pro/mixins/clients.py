from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from ..models import Client

class ClientAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only authorized users can access client views"""
    
    def test_func(self):
        user = self.request.user
        # Superusers and staff can access all clients
        if user.is_superuser or user.is_staff:
            return True
        
        # Regular users can only access their own client profile
        if hasattr(user, 'client'):
            client = self.get_object()
            return user.client == client
        
        return False
    
    def handle_no_permission(self):
        raise PermissionDenied("You don't have permission to access this client.")

class ClientFormMixin:
    """Mixin to handle common form processing for Client views"""
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Add custom form validation logic here if needed
        return super().form_valid(form)

class ClientSuccessUrlMixin:
    """Mixin to provide success URLs for Client views"""
    
    def get_success_url(self):
        # You can customize the success URL based on user type
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse_lazy('data_pro:client-list')
        return reverse_lazy('data_pro:dashboard')