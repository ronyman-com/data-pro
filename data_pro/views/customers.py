from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from data_pro.models.customers import *
from data_pro.forms.customers import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import csv
import io

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'admin/customers/list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/create.html'
    success_url = reverse_lazy('data_pro:customer-list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/update.html'
    success_url = reverse_lazy('data_pro:customer-list')

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'admin/customers/delete.html'
    success_url = reverse_lazy('data_pro:customer-list')


class CustomerImportView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'error': 'File is not CSV type'}, status=400)
            
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            
            # Skip header if needed
            next(io_string)
            
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                # Create customer from CSV data
                # Adjust this part according to your Customer model fields
                _, created = Customer.objects.update_or_create(
                    id=column[0],
                    defaults={
                        'name': column[1],
                        'email': column[2],
                        # Add other fields as needed
                    }
                )
            
            return JsonResponse({'message': 'Customers imported successfully'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CustomerExportView(View):
    def get(self, request, *args, **kwargs):
        try:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
            
            writer = csv.writer(response)
            # Write CSV header
            writer.writerow(['ID', 'Name', 'Email'])  # Adjust fields as per your model
            
            customers = Customer.objects.all().values_list('id', 'name', 'email')  # Adjust fields
            
            for customer in customers:
                writer.writerow(customer)
            
            return response
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CustomerStatusView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            return JsonResponse({
                'id': customer.id,
                'status': customer.status,  # Assuming your model has a status field
                'name': customer.name
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            new_status = request.POST.get('status')
            
            # Validate status if needed
            # if new_status not in [choices...]:
            #     return JsonResponse({'error': 'Invalid status'}, status=400)
            
            customer.status = new_status
            customer.save()
            
            return JsonResponse({
                'message': 'Status updated successfully',
                'new_status': customer.status
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)