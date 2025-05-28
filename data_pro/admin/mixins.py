# data_pro/admin/mixins.py (recommended to create this separate file)
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

class BaseAccessMixin:
    """Base class for all access mixins"""
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(f'{settings.LOGIN_URL}?next={self.request.path}')
        return self.handle_denied()
    
    def handle_denied(self):
        messages.error(self.request, self.get_denied_message())
        return redirect(self.get_redirect_url())
    
    def get_denied_message(self):
        return "Access denied"
    
    def get_redirect_url(self):
        return 'system:home'

class SuperAdminMixin(BaseAccessMixin):
    """Only allows superusers (is_superuser=True)"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def get_denied_message(self):
        return "Superadmin access required"

class ClientAdminMixin(BaseAccessMixin):
    """Allows both superusers and client admins"""
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or 
               getattr(request.user, 'user_type', None) == 'CLIENT_ADMIN'):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def get_denied_message(self):
        return "Client admin access required"

class StaffAccessMixin(BaseAccessMixin):
    """Allows staff users (is_staff=True)"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def get_denied_message(self):
        return "Staff access required"