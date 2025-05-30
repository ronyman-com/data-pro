from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings

# Import models directly
from data_pro.models.customers import Customer
from data_pro.models.visas import Visa
from data_pro.models.passports import Passport, PassportExtension
from data_pro.models.invoices import Invoice
from data_pro.models.vehicles import Vehicle
from data_pro.models.transports import Transport

class SystemLandingView(LoginRequiredMixin, TemplateView):
    """System dashboard view showing key metrics and quick actions"""
    
    template_name = 'admin/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # Safely check user_type with fallback
        user_type = getattr(user, 'user_type', None)
        
        # Get filtered querysets based on user type
        if user_type == 'admin':  # Now using the safely accessed user_type
            customers = Customer.objects.all()
            visas = Visa.objects.all()
            passports = Passport.objects.all()
            extensions = PassportExtension.objects.all()
            vehicles = Vehicle.objects.all()
            transports = Transport.objects.all()
        else:
            # Add additional safety check for client attribute
            client_filter = {}
            if hasattr(user, 'client'):
                client_filter = {'client': user.client}
            
            customers = Customer.objects.filter(**client_filter)
            visas = Visa.objects.filter(customer__client=user.client) if hasattr(user, 'client') else Visa.objects.none()
            passports = Passport.objects.filter(customer__client=user.client) if hasattr(user, 'client') else Passport.objects.none()
            extensions = PassportExtension.objects.filter(passport__customer__client=user.client) if hasattr(user, 'client') else PassportExtension.objects.none()
            vehicles = Vehicle.objects.filter(**client_filter)
            transports = Transport.objects.filter(**client_filter)

        # Prepare dashboard statistics
        context.update({
            'total_customers': customers.count(),
            'active_visas': visas.filter(status='approved').count(),
            'pending_passports': passports.filter(status='pending').count(),
            'pending_extensions': extensions.filter(released_date__isnull=True).count(),
            'available_vehicles': vehicles.filter(status='available').count(),
            'active_transports': transports.filter(
                status__in=['scheduled', 'in_progress']
            ).count(),
            'recent_invoices': Invoice.objects.filter(
                **client_filter
            ).order_by('-issue_date')[:5] if hasattr(user, 'client') else Invoice.objects.none(),
        })

        # Prepare quick actions
        context['quick_actions'] = self._get_quick_actions(user, passports.exists() if passports else False)

        return context

    def _get_quick_actions(self, user, has_passports):
        """Generate quick action links based on user permissions"""
        actions = [
            {'name': 'Add Customer', 'url': 'data_pro:customer-create', 'icon': 'bi-person-plus'},
            {'name': 'Create Visa', 'url': 'data_pro:visa-create', 'icon': 'bi-passport'},
            {'name': 'New Invoice', 'url': 'data_pro:invoice-create', 'icon': 'bi-receipt'},
            {'name': 'Schedule Transport', 'url': 'data_pro:transport-create', 'icon': 'bi-truck'},
        ]

        # Add admin-only actions (using getattr for safety)
        if getattr(user, 'user_type', None) == 'admin':
            actions.extend([
                {'name': 'Add Client', 'url': 'data_pro:client-create', 'icon': 'bi-building'},
                {'name': 'Register Vehicle', 'url': 'data_pro:vehicle-create', 'icon': 'bi-car-front'},
            ])

        # Add passport extension action if applicable
        if has_passports:
            actions.append(
                {'name': 'Apply Passport Extension', 
                 'url': 'data_pro:passport-extension-create', 
                 'icon': 'bi-file-earmark-plus'}
            )

        return actions