from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
import csv
import io

from data_pro.models.customers import Customer
from data_pro.models.clients import Client
from data_pro.forms.customers import CustomerForm

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'admin/customers/list.html'
    context_object_name = 'customers'
    paginate_by = 25


    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(client=self.request.user.client)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        return queryset.select_related('client')

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/create.html'
    success_url = reverse_lazy('data_pro:customer-list')

    def form_valid(self, form):
        # Get the user's profile
        user_profile = self.request.user.profile
        
        # Set client based on user type
        if user_profile.user_type == 'client_admin':
            form.instance.client = user_profile.client
        elif not self.request.user.is_superuser:
            messages.error(self.request, 'Only client admins or superusers can create customers')
            return self.form_invalid(form)
        
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Customer created successfully!')
        return super().form_valid(form)
class CustomerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/update.html'
    success_url = reverse_lazy('data_pro:customer-list')

    def test_func(self):
        customer = self.get_object()
        return self.request.user.is_superuser or customer.client == self.request.user.client

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully!')
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Customer
    template_name = 'admin/customers/delete.html'
    success_url = reverse_lazy('data_pro:customer-list')

    def test_func(self):
        customer = self.get_object()
        return self.request.user.is_superuser or customer.client == self.request.user.client

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Customer deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CustomerImportView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'error': 'File must be a CSV'}, status=400)
            
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string)
            
            for row in reader:
                Customer.objects.create(
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                    email=row.get('email', ''),
                    phone=row.get('phone', ''),
                    client=request.user.client if not request.user.is_superuser else Client.objects.get(id=row.get('client_id')),
                    status=row.get('status', 'active'),
                    created_by=request.user
                )
            
            return JsonResponse({'message': 'Customers imported successfully'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class CustomerExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'First Name', 'Last Name', 'Email', 'Phone', 
                'Status', 'Client', 'Created At'
            ])
            
            queryset = Customer.objects.all()
            if not request.user.is_superuser:
                queryset = queryset.filter(client=request.user.client)
            
            for customer in queryset:
                writer.writerow([
                    customer.id,
                    customer.first_name,
                    customer.last_name,
                    customer.email,
                    customer.phone,
                    customer.get_status_display(),
                    customer.client.name if customer.client else '',
                    customer.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class CustomerStatusView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            if not request.user.is_superuser and customer.client != request.user.client:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            return JsonResponse({
                'id': customer.id,
                'status': customer.status,
                'full_name': str(customer)
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            if not request.user.is_superuser and customer.client != request.user.client:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            new_status = request.POST.get('status')
            if new_status not in dict(Customer.STATUS_CHOICES).keys():
                return JsonResponse({'error': 'Invalid status'}, status=400)
            
            customer.status = new_status
            customer.save()
            
            return JsonResponse({
                'message': 'Status updated successfully',
                'new_status': customer.get_status_display()
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)