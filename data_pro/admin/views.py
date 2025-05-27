from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from data_pro.core.models import Customer, Visa, Passport, Vehicle, Invoice, TransportService
from data_pro.utils.excel_handlers import ExcelImporter, ExcelExporter
import datetime

class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'SUPERADMIN'

class ClientAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type in ['SUPERADMIN', 'CLIENT_ADMIN']

class CustomerListView(ClientAdminRequiredMixin, ListView):
    model = Customer
    template_name = 'admin/customer_list.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

class CustomerCreateView(ClientAdminRequiredMixin, CreateView):
    model = Customer
    fields = '__all__'
    template_name = 'admin/customer_form.html'
    success_url = reverse_lazy('admin:customer-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class CustomerUpdateView(ClientAdminRequiredMixin, UpdateView):
    model = Customer
    fields = '__all__'
    template_name = 'admin/customer_form.html'
    success_url = reverse_lazy('admin:customer-list')
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class CustomerImportView(ClientAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        excel_file = request.FILES['excel_file']
        importer = ExcelImporter(Customer, request.user)
        try:
            importer.import_from_excel(excel_file)
            messages.success(request, 'Customers imported successfully')
        except Exception as e:
            messages.error(request, f'Error importing customers: {str(e)}')
        return redirect('admin:customer-list')

class CustomerExportView(ClientAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        exporter = ExcelExporter()
        excel_file = exporter.export_to_excel(queryset)
        
        response = HttpResponse(
            excel_file.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=customers_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'
        return response
    
    def get_queryset(self):
        qs = Customer.objects.all()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

# Similar views for Visa, Passport, Vehicle, Invoice, TransportService would be implemented