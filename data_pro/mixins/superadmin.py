from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only superusers can access the view"""
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        raise PermissionDenied("You must be a superadmin to access this page.")

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only staff members can access the view"""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        raise PermissionDenied("You must be staff to access this page.")

class AdminFormMixin:
    """Common form mixin for admin views"""
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add any additional form kwargs needed for admin views
        return kwargs
    
    def form_valid(self, form):
        # Add any admin-specific form validation logic
        return super().form_valid(form)

class AdminSuccessUrlMixin:
    """Mixin to provide success URLs for admin views"""
    
    def get_success_url(self):
        # Default to dashboard, can be overridden in specific views
        return reverse_lazy('data_pro:dashboard')