from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from data_pro.core.models import (
    Customer, 
    Visa, 
    Passport, 
    Invoice, 
    Vehicle, 
    TransportService
)

class SystemLandingView(LoginRequiredMixin, TemplateView):
    """
    Main landing page view for the Data-Pro system
    Shows key metrics and quick access to all modules
    """
    template_name = 'admin/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Statistics for dashboard cards
        if user.user_type == 'SUPERADMIN':
            context.update({
                'total_customers': Customer.objects.count(),
                'active_visas': Visa.objects.count(),
                'pending_passports': Passport.objects.filter(release_date__isnull=True).count(),
                'recent_invoices': Invoice.objects.order_by('-issue_date')[:5],
                'available_vehicles': Vehicle.objects.filter(is_available=True).count(),
                'scheduled_transports': TransportService.objects.filter(is_completed=False).count(),
            })
        elif user.user_type == 'CLIENT_ADMIN':
            context.update({
                'total_customers': Customer.objects.filter(created_by__client=user.client).count(),
                'active_visas': Visa.objects.filter(created_by__client=user.client).count(),
                'pending_passports': Passport.objects.filter(
                    created_by__client=user.client,
                    release_date__isnull=True
                ).count(),
                'recent_invoices': Invoice.objects.filter(
                    created_by__client=user.client
                ).order_by('-issue_date')[:5],
                'available_vehicles': Vehicle.objects.filter(
                    created_by__client=user.client,
                    is_available=True
                ).count(),
                'scheduled_transports': TransportService.objects.filter(
                    created_by__client=user.client,
                    is_completed=False
                ).count(),
            })

        # Quick action links
        context['quick_actions'] = [
            {'name': 'Add Customer', 'url': 'system:customer-create', 'icon': 'bi-person-plus'},
            {'name': 'Create Visa', 'url': 'system:visa-create', 'icon': 'bi-passport'},
            {'name': 'New Invoice', 'url': 'system:invoice-create', 'icon': 'bi-receipt'},
            {'name': 'Schedule Transport', 'url': 'system:transport-create', 'icon': 'bi-truck'},
        ]

        return context