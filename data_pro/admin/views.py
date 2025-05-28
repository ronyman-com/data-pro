from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from datetime import datetime
# In data_pro/views.py
from django.shortcuts import render

from data_pro.core.models import Customer, Visa, Passport, Vehicle, Invoice, TransportService, Office, Airport
from data_pro.utils.excel_handlers import ExcelImporter, ExcelExporter
from data_pro.models import User
from django.core.exceptions import PermissionDenied


from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory
from django.db.models import Sum


from data_pro.admin.forms import *
from data_pro.admin.mixins import *


def permission_denied_view(request, exception):
    return render(request, 'admin/403.html', status=403)



# ====================== ADMIN VIEWS ======================
# data_pro/admin/views.py
class ClientUserListView(SuperAdminMixin, ListView):
    model = User
    template_name = 'admin/users/client_list.html'
    
    def get_queryset(self):
        return User.objects.filter(user_type='CLIENT_ADMIN')

class ClientUserCreateView(SuperAdminMixin, CreateView):
    model = User
    fields = ['username', 'email', 'password', 'user_type', 'client']
    template_name = 'admin/users/client_form.html'
    success_url = reverse_lazy('system:client-user-list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.user_type = 'CLIENT_ADMIN'
        user.save()
        return super().form_valid(form)
    

class UserListView(SuperAdminMixin, ListView):
    template_name = 'admin/users/list.html'
    model = User
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

class SuperAdminPanelView(SuperAdminMixin, TemplateView):
    template_name = 'admin/superadmin_panel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add superadmin management data
        return context
    
# data_pro/admin/views.py
class SystemSettingsView(SuperAdminMixin, TemplateView):
    template_name = 'admin/system_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any system settings context data here
        return context

class DashboardView(ClientAdminMixin, TemplateView):
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        context['is_client_admin'] = (
            not self.request.user.is_superuser and 
            getattr(self.request.user, 'user_type', None) == 'CLIENT_ADMIN'
        )
        
        # Add your dashboard statistics
        if self.request.user.is_superuser:
            context['customer_count'] = Customer.objects.count()
            context['recent_customers'] = Customer.objects.order_by('-created_at')[:5]
        else:
            context['customer_count'] = Customer.objects.filter(
                created_by__client=self.request.user.client
            ).count()
            context['recent_customers'] = Customer.objects.filter(
                created_by__client=self.request.user.client
            ).order_by('-created_at')[:5]
            
        return context

class ClientAdminRequiredMixin:
    """Verify that the current user is a client admin."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if not self.is_client_admin(request.user):
            raise PermissionDenied("Client admin access required")
            
        return super().dispatch(request, *args, **kwargs)
    
    def is_client_admin(self, user):
        # Check if user is either SUPERADMIN or CLIENT_ADMIN
        return user.user_type in ['SUPERADMIN', 'CLIENT_ADMIN']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Client admin access required")
            return redirect('system:home')  # Or your preferred redirect
        return redirect(settings.LOGIN_URL)


# ====================== CUSTOMER VIEWS ======================
class CustomerListView(ClientAdminMixin, ListView):
    model = Customer
    template_name = 'admin/customers/list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('created_by')
        if not self.request.user.is_superuser:
            qs = qs.filter(created_by__client=self.request.user.client)
        
        if search := self.request.GET.get('search'):
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        return qs



class CustomerCreateView(ClientAdminRequiredMixin, CreateView):
    model = Customer
    template_name = 'admin/customers/form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth', 'nationality']
    success_url = reverse_lazy('system:customer-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Customer created successfully')
        return super().form_valid(form)

class CustomerDetailView(ClientAdminRequiredMixin, DetailView):
    model = Customer
    template_name = 'admin/customers/detail.html'
    context_object_name = 'customer'

class CustomerUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = Customer
    template_name = 'admin/customers/form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth', 'nationality']
    
    def get_success_url(self):
        messages.success(self.request, 'Customer updated successfully')
        return reverse_lazy('system:customer-detail', kwargs={'pk': self.object.pk})

class CustomerStatusView(ClientAdminRequiredMixin, UpdateView):
    model = Customer
    fields = ['is_active']
    template_name = 'admin/customers/status.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Customer status updated successfully')
        return reverse_lazy('system:customer-list')

class CustomerDeleteView(ClientAdminRequiredMixin, DeleteView):
    model = Customer
    template_name = 'admin/customers/confirm_delete.html'
    success_url = reverse_lazy('system:customer-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Customer deleted successfully')
        return super().delete(request, *args, **kwargs)

class CustomerImportView(ClientAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'excel_file' not in request.FILES:
            messages.error(request, 'No file uploaded')
            return redirect('system:customer-list')
            
        excel_file = request.FILES['excel_file']
        importer = ExcelImporter(Customer, request.user)
        
        try:
            imported_count = len(importer.import_from_excel(excel_file))
            messages.success(request, f'Successfully imported {imported_count} customers')
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        return redirect('system:customer-list')

class CustomerExportView(ClientAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        exporter = ExcelExporter()
        
        try:
            excel_file = exporter.export_to_excel(queryset)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            response = HttpResponse(
                excel_file.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename=customers_export_{timestamp}.xlsx'
            return response
            
        except Exception as e:
            messages.error(request, f'Export failed: {str(e)}')
            return redirect('system:customer-list')
    
    def get_queryset(self):
        qs = Customer.objects.all().select_related('created_by')
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

# ====================== VISA VIEWS ======================
class VisaListView(ClientAdminRequiredMixin, ListView):
    model = Visa
    template_name = 'admin/visas/list.html'
    context_object_name = 'visas'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('customer', 'passport')
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

class VisaCreateView(ClientAdminRequiredMixin, CreateView):
    model = Visa
    template_name = 'admin/visas/form.html'
    fields = ['customer', 'passport', 'visa_type', 'country', 'issue_date', 'expiry_date', 'status']
    success_url = reverse_lazy('system:visa-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Visa created successfully')
        return super().form_valid(form)

class VisaUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = Visa
    template_name = 'admin/visas/form.html'
    fields = ['customer', 'passport', 'visa_type', 'country', 'issue_date', 'expiry_date', 'status']
    
    def get_success_url(self):
        messages.success(self.request, 'Visa updated successfully')
        return reverse_lazy('system:visa-list')

class VisaStatusView(ClientAdminRequiredMixin, UpdateView):
    model = Visa
    fields = ['status']
    template_name = 'admin/visas/status.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Visa status updated successfully')
        return reverse_lazy('system:visa-list')

class VisaDeleteView(ClientAdminRequiredMixin, DeleteView):
    model = Visa
    template_name = 'admin/visas/confirm_delete.html'
    success_url = reverse_lazy('system:visa-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Visa deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================== PASSPORT VIEWS ======================
class PassportListView(ClientAdminRequiredMixin, ListView):
    model = Passport
    template_name = 'admin/passports/list.html'
    context_object_name = 'passports'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('customer')
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs


# ====================== INVOICE VIEWS ======================
class InvoiceListView(ClientAdminRequiredMixin, ListView):
    model = Invoice
    template_name = 'admin/invoices/list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('customer')
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        
        # Search functionality
        if search := self.request.GET.get('search'):
            qs = qs.filter(
                Q(invoice_number__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search)
            )
        return qs

class InvoiceCreateView(ClientAdminRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'admin/invoices/create.html'
    success_url = reverse_lazy('system:invoice-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InvoiceItemFormSet = inlineformset_factory(
            Invoice, InvoiceItem, 
            form=InvoiceItemForm, 
            extra=1,
            can_delete=True
        )
        if self.request.POST:
            context['invoice_item_formset'] = InvoiceItemFormSet(self.request.POST)
        else:
            context['invoice_item_formset'] = InvoiceItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        invoice_item_formset = context['invoice_item_formset']
        form.instance.created_by = self.request.user
        
        if invoice_item_formset.is_valid():
            self.object = form.save()
            invoice_item_formset.instance = self.object
            invoice_item_formset.save()
            
            # Calculate and save total amount
            total = self.object.items.aggregate(
                total=Sum('quantity') * Sum('unit_price')
            )['total'] or 0
            self.object.total_amount = total
            self.object.save()
            
            messages.success(self.request, 'Invoice created successfully')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class InvoiceDetailView(ClientAdminRequiredMixin, DetailView):
    model = Invoice
    template_name = 'admin/invoices/detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

class InvoiceUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'admin/invoices/update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        InvoiceItemFormSet = inlineformset_factory(
            Invoice, InvoiceItem, 
            form=InvoiceItemForm, 
            extra=1,
            can_delete=True
        )
        if self.request.POST:
            context['invoice_item_formset'] = InvoiceItemFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['invoice_item_formset'] = InvoiceItemFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        invoice_item_formset = context['invoice_item_formset']
        
        if invoice_item_formset.is_valid():
            self.object = form.save()
            invoice_item_formset.instance = self.object
            invoice_item_formset.save()
            
            # Recalculate total amount
            total = self.object.items.aggregate(
                total=Sum('quantity') * Sum('unit_price')
            )['total'] or 0
            self.object.total_amount = total
            self.object.save()
            
            messages.success(self.request, 'Invoice updated successfully')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('system:invoice-detail', kwargs={'pk': self.object.pk})

class InvoiceStatusView(ClientAdminRequiredMixin, UpdateView):
    model = Invoice
    fields = ['status', 'paid_amount', 'paid_date', 'payment_method', 'payment_notes']
    template_name = 'admin/invoices/status.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Invoice status updated successfully')
        return response

    def get_success_url(self):
        return reverse_lazy('system:invoice-detail', kwargs={'pk': self.object.pk})

class InvoiceDeleteView(ClientAdminRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'admin/invoices/delete.html'
    success_url = reverse_lazy('system:invoice-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Invoice deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================== VEHICLE VIEWS ======================
class VehicleListView(ClientAdminRequiredMixin, ListView):
    model = Vehicle
    template_name = 'admin/vehicles/list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

class VehicleCreateView(ClientAdminRequiredMixin, CreateView):
    model = Vehicle
    template_name = 'admin/vehicles/form.html'
    fields = ['make', 'model', 'year', 'license_plate', 'capacity', 'status']
    success_url = reverse_lazy('system:vehicle-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Vehicle created successfully')
        return super().form_valid(form)

class VehicleDetailView(ClientAdminRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'admin/vehicles/detail.html'
    context_object_name = 'vehicle'

class VehicleUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = Vehicle
    template_name = 'admin/vehicles/form.html'
    fields = ['make', 'model', 'year', 'license_plate', 'capacity', 'status']
    
    def get_success_url(self):
        messages.success(self.request, 'Vehicle updated successfully')
        return reverse_lazy('system:vehicle-detail', kwargs={'pk': self.object.pk})

class VehicleStatusView(ClientAdminRequiredMixin, UpdateView):
    model = Vehicle
    fields = ['status']
    template_name = 'admin/vehicles/status.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Vehicle status updated successfully')
        return reverse_lazy('system:vehicle-list')

class VehicleDeleteView(ClientAdminRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'admin/vehicles/confirm_delete.html'
    success_url = reverse_lazy('system:vehicle-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vehicle deleted successfully')
        return super().delete(request, *args, **kwargs)

# ====================== TRANSPORT SERVICE VIEWS ======================
class TransportListView(ClientAdminRequiredMixin, ListView):
    model = TransportService
    template_name = 'admin/transports/list.html'
    context_object_name = 'transports'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('customer', 'vehicle')
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

class TransportCreateView(ClientAdminRequiredMixin, CreateView):
    model = TransportService
    template_name = 'admin/transports/form.html'
    fields = ['customer', 'vehicle', 'pickup_location', 'dropoff_location', 'pickup_time', 'dropoff_time', 'status']
    success_url = reverse_lazy('system:transport-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Transport service created successfully')
        return super().form_valid(form)

class TransportDetailView(ClientAdminRequiredMixin, DetailView):
    model = TransportService
    template_name = 'admin/transports/detail.html'
    context_object_name = 'transport'

class TransportUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = TransportService
    template_name = 'admin/transports/form.html'
    fields = ['customer', 'vehicle', 'pickup_location', 'dropoff_location', 'pickup_time', 'dropoff_time', 'status']
    
    def get_success_url(self):
        messages.success(self.request, 'Transport service updated successfully')
        return reverse_lazy('system:transport-detail', kwargs={'pk': self.object.pk})

class TransportStatusView(ClientAdminRequiredMixin, UpdateView):
    model = TransportService
    fields = ['status']
    template_name = 'admin/transports/status.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Transport status updated successfully')
        return reverse_lazy('system:transport-list')

class TransportDeleteView(ClientAdminRequiredMixin, DeleteView):
    model = TransportService
    template_name = 'admin/transports/confirm_delete.html'
    success_url = reverse_lazy('system:transport-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transport service deleted successfully')
        return super().delete(request, *args, **kwargs)